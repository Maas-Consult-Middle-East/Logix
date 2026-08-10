import frappe
from frappe.utils import now_datetime, nowdate


DEMO_PREFIX = "LOGIX-DEMO"


def _get_or_create(doctype, filters, values=None):
	name = frappe.db.get_value(doctype, filters, "name")
	if name:
		return frappe.get_doc(doctype, name)
	doc = frappe.get_doc({"doctype": doctype, **filters, **(values or {})})
	doc.insert(ignore_permissions=True)
	return doc


def execute():
	"""Create a linked, repeatable development dataset for every implemented Logix DocType."""
	frappe.set_user("Administrator")

	settings = frappe.get_single("Logix Settings")
	settings.update({
		"manual_pricing_allowed": 1,
		"rate_card_pricing_enabled": 1,
		"vehicle_capacity_behavior": "Warn",
		"default_public_tracking_expiry_days": 30,
	})
	settings.save(ignore_permissions=True)

	branch = _get_or_create("Branch", {"branch": "Logix Demo Branch"})
	group = _get_or_create(
		"Customer Group", {"customer_group_name": "Logix Demo Customers"}, {"is_group": 0}
	)
	customer = _get_or_create(
		"Customer",
		{"customer_name": "Logix Demo Customer"},
		{"customer_type": "Company", "customer_group": group.name, "logix_default_branch": branch.name},
	)

	origin = _get_or_create("Logix City", {"city_name": "Riyadh Demo"}, {"country": "Saudi Arabia"})
	hub = _get_or_create("Logix City", {"city_name": "Al Ahsa Demo"}, {"country": "Saudi Arabia"})
	destination = _get_or_create("Logix City", {"city_name": "Dammam Demo"}, {"country": "Saudi Arabia"})
	load_type = _get_or_create(
		"Logix Load Type", {"load_type_name": "General Cargo Demo"}, {"description": "Demonstration general cargo"}
	)
	vehicle_type = _get_or_create(
		"Logix Vehicle Type",
		{"vehicle_type_name": "10 Ton Demo"},
		{"weight_capacity_kg": 10000, "volume_capacity_cbm": 45, "pallet_capacity": 20},
	)
	route = _get_or_create(
		"Logix Route",
		{"from_city": origin.name, "to_city": destination.name},
		{"typical_distance_km": 410, "typical_duration_minutes": 300, "active": 1},
	)
	currency = frappe.db.get_single_value("Global Defaults", "default_currency") or "SAR"
	_get_or_create(
		"Logix Transport Rate Card",
		{"customer": customer.name, "from_city": origin.name, "to_city": destination.name},
		{
			"vehicle_type": vehicle_type.name, "load_type": load_type.name, "base_rate": 2200,
			"included_weight": 5000, "excess_rate": 100, "extra_stop_charge": 250,
			"minimum_freight": 2000, "currency": currency, "effective_from": nowdate(),
		},
	)

	estimation = _get_or_create(
		"Logix Estimation",
		{"customer": customer.name, "branch": branch.name, "notes": f"{DEMO_PREFIX} commercial estimate"},
		{"status": "Accepted", "estimated_revenue": 2200, "estimated_direct_cost": 1500},
	)
	job = _get_or_create(
		"Logix Job",
		{"customer": customer.name, "branch": branch.name, "closure_reason": DEMO_PREFIX},
		{
			"estimation": estimation.name, "status": "Confirmed", "from_city": origin.name,
			"to_city": destination.name, "route": route.name, "load_type": load_type.name,
			"preferred_vehicle_type": vehicle_type.name, "agreed_revenue": 2200, "estimated_cost": 1500,
		},
	)
	if estimation.downstream_job != job.name:
		estimation.db_set({"status": "Accepted", "downstream_job": job.name})

	order = _get_or_create(
		"Logix Shipment Order",
		{"job": job.name, "customer": customer.name, "branch": branch.name},
		{"status": "Released", "quantity": 20, "weight_kg": 8000, "cbm": 30, "pallets": 20},
	)
	shipment_name = frappe.db.get_value("Logix Shipment", {"job": job.name}, "name")
	if shipment_name:
		shipment = frappe.get_doc("Logix Shipment", shipment_name)
	else:
		shipment = frappe.get_doc({
			"doctype": "Logix Shipment", "job": job.name, "shipment_order": order.name,
			"customer": customer.name, "branch": branch.name, "status": "Ready for Planning",
			"load_type": load_type.name, "total_quantity": 20, "weight_kg": 8000,
			"cbm": 30, "pallets": 20, "tracking_enabled": 1,
			"stops": [
				{"sequence": 1, "stop_type": "Pickup", "city": origin.name, "location_text": "Demo Origin Depot"},
				{"sequence": 2, "stop_type": "Handover", "city": hub.name, "location_text": "Demo Hub"},
				{"sequence": 3, "stop_type": "Delivery", "city": destination.name, "location_text": "Demo Customer Site", "pod_required": 1},
			],
		}).insert(ignore_permissions=True)

	leg1 = _get_or_create(
		"Logix Shipment Leg", {"shipment": shipment.name, "sequence": 1},
		{"from_stop_sequence": 1, "to_stop_sequence": 2, "status": "Assigned", "handover_required": 1},
	)
	leg2 = _get_or_create(
		"Logix Shipment Leg", {"shipment": shipment.name, "sequence": 2},
		{"from_stop_sequence": 2, "to_stop_sequence": 3, "status": "Pending"},
	)

	trip1 = _demo_trip(branch.name, shipment, leg1, 12, "Company Owned")
	trip2 = _demo_trip(branch.name, shipment, leg2, 8, "Outsourced Transport Service")
	_get_or_create(
		"Logix Handover", {"shipment": shipment.name, "from_leg": leg1.name, "to_leg": leg2.name},
		{"from_trip": trip1.name, "to_trip": trip2.name, "handover_time": now_datetime(), "notes": DEMO_PREFIX},
	)
	_get_or_create(
		"Logix Shipment Event", {"shipment": shipment.name, "event_type": "Demo Shipment Created"},
		{"trip": trip1.name, "event_time": now_datetime(), "event_user": "Administrator", "new_status": shipment.status},
	)

	frappe.db.commit()
	return {
		"branch": branch.name, "customer": customer.name, "estimation": estimation.name,
		"job": job.name, "shipment_order": order.name, "shipment": shipment.name,
		"shipment_legs": [leg1.name, leg2.name], "trips": [trip1.name, trip2.name],
	}


def _demo_trip(branch, shipment, leg, quantity, resource_mode):
	existing = frappe.db.get_value("Logix Trip Shipment Allocation", {"shipment_leg": leg.name}, "parent")
	if existing:
		return frappe.get_doc("Logix Trip", existing)
	return frappe.get_doc({
		"doctype": "Logix Trip", "branch": branch, "status": "Planned", "resource_mode": resource_mode,
		"vendor_vehicle": "Demo Vendor Truck" if resource_mode.startswith("Outsourced") else None,
		"vendor_driver": "Demo Vendor Driver" if resource_mode.startswith("Outsourced") else None,
		"allocations": [{
			"shipment": shipment.name, "shipment_leg": leg.name, "allocated_quantity": quantity,
			"weight_kg": shipment.weight_kg * quantity / shipment.total_quantity,
			"cbm": shipment.cbm * quantity / shipment.total_quantity,
			"pallets": quantity, "pickup_stop_sequence": leg.from_stop_sequence,
			"delivery_stop_sequence": leg.to_stop_sequence, "status": "Planned",
		}],
	}).insert(ignore_permissions=True)
