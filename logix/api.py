import secrets

import erpnext
import frappe
from erpnext import get_company_currency
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, flt, getdate, now_datetime, nowdate


def _validate_estimation_for_job(estimation):
	if estimation.docstatus != 1:
		frappe.throw(_("Only submitted Estimations can be used to create a Job."))
	if estimation.status != "Accepted":
		frappe.throw(_("Only an Accepted Estimation can be used to create a Job."))
	if estimation.valid_until and getdate(estimation.valid_until) < getdate(nowdate()):
		frappe.throw(_("A Job cannot be created from an expired Estimation."))
	existing_job = frappe.db.get_value("Logix Job", {"estimation": estimation.name}, "name")
	if existing_job:
		frappe.throw(_("Job {0} has already been created from this Estimation.").format(existing_job))


def _set_job_commercials(source, target):
	operational_row = next((row for row in source.items if row.from_city and row.to_city), None)
	if not operational_row:
		frappe.throw(_("At least one Estimation Item must provide From and To before creating a Job."))
	target.from_city = operational_row.from_city
	target.to_city = operational_row.to_city
	target.preferred_vehicle_type = operational_row.vehicle_type
	target.load_type = operational_row.load_type
	target.contract_rate = source.contract_rate
	target.currency = source.currency
	target.commercial_net_total = source.net_total
	target.additional_discount_amount = source.additional_discount_amount
	target.discount_basis = source.apply_discount_on
	target.total_taxes_and_charges = source.total_taxes_and_charges
	target.agreed_revenue = source.grand_total
	target.estimated_cost = source.estimated_direct_cost
	target.estimation_item_summary = "\n".join(
		_(("{0}: {1} ({2})")).format(row.bill_by, row.description or "", frappe.format_value(row.amount, {"fieldtype": "Currency", "options": source.currency}))
		for row in source.items
	)


@frappe.whitelist()
def make_job(source_name, target_doc=None):
	"""Map a submitted Estimation to a new or existing Job draft."""
	estimation = frappe.get_doc("Logix Estimation", source_name)
	estimation.check_permission("read")
	_validate_estimation_for_job(estimation)

	return get_mapped_doc(
		"Logix Estimation",
		source_name,
		{
			"Logix Estimation": {
				"doctype": "Logix Job",
				"field_map": {
					"name": "estimation",
					"grand_total": "agreed_revenue",
				},
				"field_no_map": ["naming_series", "status"],
				"validation": {"docstatus": ["=", 1]},
			},
		},
		target_doc,
		postprocess=_set_job_commercials,
	)


def _set_shipment_stops_from_job(source, target):
	"""Seed the required pickup and delivery stops from the Job route."""
	target.append("stops", {"sequence": 1, "stop_type": "Pickup", "city": source.from_city})
	target.append("stops", {"sequence": 2, "stop_type": "Delivery", "city": source.to_city})


@frappe.whitelist()
def make_shipment_order(source_name, target_doc=None):
	"""Map an active Job to a new Shipment Order draft."""
	job = frappe.get_doc("Logix Job", source_name)
	job.check_permission("read")

	if job.docstatus == 2:
		frappe.throw(_("A cancelled Job cannot be used to create a Shipment Order."))

	return get_mapped_doc(
		"Logix Job",
		source_name,
		{
			"Logix Job": {
				"doctype": "Logix Shipment Order",
				"field_map": {"name": "job"},
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
	)


@frappe.whitelist()
def make_shipment(source_name, target_doc=None):
	"""Map an active Job to a new Shipment draft."""
	job = frappe.get_doc("Logix Job", source_name)
	job.check_permission("read")

	if job.docstatus == 2:
		frappe.throw(_("A cancelled Job cannot be used to create a Shipment."))

	return get_mapped_doc(
		"Logix Job",
		source_name,
		{
			"Logix Job": {
				"doctype": "Logix Shipment",
				"field_map": {"name": "job"},
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess=_set_shipment_stops_from_job,
	)


@frappe.whitelist()
def make_shipment_from_order(source_name, target_doc=None):
	"""Map an active Shipment Order to a new Shipment draft."""
	order = frappe.get_doc("Logix Shipment Order", source_name)
	order.check_permission("read")

	if order.docstatus == 2:
		frappe.throw(_("A cancelled Shipment Order cannot be used to create a Shipment."))

	job = frappe.get_doc("Logix Job", order.job)
	job.check_permission("read")
	if job.docstatus == 2:
		frappe.throw(_("A Shipment requires an active Job."))

	def set_shipment_defaults(source, target):
		target.load_type = job.load_type
		_set_shipment_stops_from_job(job, target)

	return get_mapped_doc(
		"Logix Shipment Order",
		source_name,
		{
			"Logix Shipment Order": {
				"doctype": "Logix Shipment",
				"field_map": {"name": "shipment_order", "quantity": "total_quantity"},
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess=set_shipment_defaults,
	)


def _append_shipment_allocation(source, target):
	"""Seed a Trip/Trip Plan allocation from a Shipment's unallocated cargo."""
	remaining_quantity = flt(source.total_quantity) - flt(source.allocated_quantity)
	if remaining_quantity <= 0:
		frappe.throw(_("Shipment {0} has no remaining cargo to allocate.").format(source.name))

	ratio = remaining_quantity / flt(source.total_quantity) if source.total_quantity else 0
	pickup_sequence = next((row.sequence for row in source.stops if row.stop_type == "Pickup"), None)
	delivery_sequence = next((row.sequence for row in reversed(source.stops) if row.stop_type == "Delivery"), None)
	target.append(
		"allocations",
		{
			"shipment": source.name,
			"job": source.job,
			"customer": source.customer,
			"allocated_quantity": remaining_quantity,
			"weight_kg": flt(source.weight_kg) * ratio,
			"cbm": flt(source.cbm) * ratio,
			"pallets": flt(source.pallets) * ratio,
			"pickup_stop_sequence": pickup_sequence,
			"delivery_stop_sequence": delivery_sequence,
		},
	)


def _validate_shipment_for_trip_creation(shipment):
	if shipment.docstatus == 2:
		frappe.throw(_("A cancelled Shipment cannot be used for trip planning."))


@frappe.whitelist()
def make_trip_plan(source_name, target_doc=None):
	"""Map a Shipment's remaining cargo to a new Trip Plan draft."""
	shipment = frappe.get_doc("Logix Shipment", source_name)
	shipment.check_permission("read")
	_validate_shipment_for_trip_creation(shipment)

	return get_mapped_doc(
		"Logix Shipment",
		source_name,
		{
			"Logix Shipment": {
				"doctype": "Logix Trip Plan",
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess=_append_shipment_allocation,
	)


@frappe.whitelist()
def make_trip_from_shipment(source_name, target_doc=None):
	"""Map a Shipment's remaining cargo directly to a new Trip draft."""
	shipment = frappe.get_doc("Logix Shipment", source_name)
	shipment.check_permission("read")
	_validate_shipment_for_trip_creation(shipment)

	return get_mapped_doc(
		"Logix Shipment",
		source_name,
		{
			"Logix Shipment": {
				"doctype": "Logix Trip",
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess=_append_shipment_allocation,
	)


@frappe.whitelist()
def make_trip_from_plan(source_name, target_doc=None):
	"""Map an active Trip Plan and its allocations to a new Trip draft."""
	trip_plan = frappe.get_doc("Logix Trip Plan", source_name)
	trip_plan.check_permission("read")
	if trip_plan.docstatus == 2 or trip_plan.status == "Cancelled":
		frappe.throw(_("A cancelled Trip Plan cannot be used to create a Trip."))

	return get_mapped_doc(
		"Logix Trip Plan",
		source_name,
		{
			"Logix Trip Plan": {
				"doctype": "Logix Trip",
				"field_map": {"name": "trip_plan"},
				"field_no_map": ["naming_series", "status"],
			},
			"Logix Trip Shipment Allocation": {
				"doctype": "Logix Trip Shipment Allocation",
			},
		},
		target_doc,
	)


@frappe.whitelist()
def make_pod(source_name, target_doc=None, shipment=None):
	"""Map one of a Trip's active Shipment allocations to a new POD draft."""
	trip = frappe.get_doc("Logix Trip", source_name)
	trip.check_permission("read")
	if trip.docstatus == 2 or trip.status == "Cancelled":
		frappe.throw(_("A cancelled Trip cannot be used to create a POD."))

	shipment = shipment or (frappe.flags.args and frappe.flags.args.get("shipment"))
	active_allocations = [row for row in trip.allocations if row.status != "Removed"]
	shipment_names = {row.shipment for row in active_allocations}
	if not shipment:
		if len(shipment_names) != 1:
			frappe.throw(_("Select a Shipment before creating the POD."))
		shipment = next(iter(shipment_names))
	if shipment not in shipment_names:
		frappe.throw(_("Shipment {0} is not actively allocated to this Trip.").format(shipment))
	if frappe.db.exists("Logix POD", {"trip": trip.name, "shipment": shipment, "docstatus": ["<", 2]}):
		frappe.throw(_("An active POD already exists for Shipment {0} on this Trip.").format(shipment))

	shipment_doc = frappe.get_doc("Logix Shipment", shipment)
	shipment_doc.check_permission("read")
	allocated_quantity = sum(
		flt(row.allocated_quantity) for row in active_allocations if row.shipment == shipment
	)

	def set_pod_defaults(source, target):
		target.trip = source.name
		target.shipment = shipment_doc.name
		target.job = shipment_doc.job
		target.customer = shipment_doc.customer
		target.branch = source.branch
		target.delivered_quantity = allocated_quantity

	if not target_doc:
		target_doc = frappe.new_doc("Logix POD")
		target_doc.branch = trip.branch

	return get_mapped_doc(
		"Logix Trip",
		source_name,
		{
			"Logix Trip": {
				"doctype": "Logix POD",
				"field_no_map": ["naming_series", "status"],
			},
		},
		target_doc,
		postprocess=set_pod_defaults,
	)


@frappe.whitelist()
def make_sales_invoice_from_pod(source_name):
	"""Create an ERPNext Sales Invoice draft for a verified POD."""
	pod = frappe.get_doc("Logix POD", source_name)
	pod.check_permission("read")
	if pod.docstatus != 1 or pod.status != "Verified":
		frappe.throw(_("Submit and verify the POD before creating a Sales Invoice."))
	if not frappe.has_permission("Sales Invoice", ptype="create"):
		frappe.throw(_("You do not have permission to create a Sales Invoice."), frappe.PermissionError)

	existing_invoice = frappe.db.exists("Sales Invoice", {"logix_pod": pod.name, "docstatus": ["<", 2]})
	if existing_invoice:
		frappe.throw(
			_("Sales Invoice {0} already exists for this POD.").format(existing_invoice)
		)

	item_code = frappe.db.get_single_value("Logix Settings", "transport_service_item")
	if not item_code:
		frappe.throw(_("Set the Transport Service Item in Logix Settings before creating an invoice."))
	item = frappe.db.get_value(
		"Item",
		item_code,
		["disabled", "is_sales_item", "item_name", "description", "stock_uom"],
		as_dict=True,
	)
	if not item or item.disabled or not item.is_sales_item:
		frappe.throw(_("The configured Transport Service Item must be an enabled sales item."))

	job = frappe.get_doc("Logix Job", pod.job)
	job.check_permission("read")
	if job.customer != pod.customer:
		frappe.throw(_("The POD Customer does not match its Job."))
	if flt(job.agreed_revenue) <= 0:
		frappe.throw(_("Set a positive Agreed Revenue on Job {0} before invoicing.").format(job.name))

	company = erpnext.get_default_company()
	if not company:
		frappe.throw(_("Set a default Company before creating a Sales Invoice."))

	invoice = frappe.new_doc("Sales Invoice")
	invoice.company = company
	invoice.currency = get_company_currency(company)
	invoice.customer = pod.customer
	invoice.customer_name = frappe.db.get_value("Customer", pod.customer, "customer_name")
	invoice.due_date = invoice.posting_date
	invoice.logix_pod = pod.name
	invoice.logix_trip = pod.trip
	invoice.logix_shipment = pod.shipment
	invoice.logix_job = pod.job
	estimation = frappe.get_doc("Logix Estimation", job.estimation) if job.estimation else None
	if hasattr(invoice, "logix_estimation"):
		invoice.logix_estimation = job.estimation
		invoice.logix_contract_rate = job.contract_rate
	invoice.currency = job.currency or invoice.currency
	commercial_rows = estimation.items if estimation else [frappe._dict({"amount":job.agreed_revenue,"description":"Transport service","bill_by":"Manual"})]
	for commercial_row in commercial_rows:
		invoice.append("items", {
			"item_code": item_code,
			"item_name": item.item_name,
			"uom": item.stock_uom,
			"conversion_factor": 1,
			"qty": 1,
			"rate": flt(commercial_row.amount),
			"description": _("{0}<br>{1}: {2}<br>Job {3}, Shipment {4}, Trip {5}, POD {6}").format(
				item.description or item.item_name, commercial_row.bill_by,
				commercial_row.description or "", pod.job, pod.shipment, pod.trip, pod.name
			),
			"income_account": frappe.db.get_value(
				"Item Default", {"parent": item_code, "company": company}, "income_account"
			)
			or frappe.db.get_value("Company", company, "default_income_account"),
			"cost_center": frappe.db.get_value(
				"Item Default", {"parent": item_code, "company": company}, "selling_cost_center"
			)
			or frappe.db.get_value("Company", company, "cost_center"),
		})
	if estimation:
		invoice.apply_discount_on = estimation.apply_discount_on
		invoice.additional_discount_percentage = estimation.additional_discount_percentage
		invoice.additional_discount_amount = estimation.additional_discount_amount
		for source_tax in estimation.taxes:
			invoice.append("taxes", {"charge_type":source_tax.charge_type,"account_head":source_tax.account_head,"description":source_tax.description,"rate":source_tax.rate,"tax_amount":source_tax.tax_amount,"included_in_print_rate":source_tax.included_in_print_rate})
	invoice.run_method("calculate_taxes_and_totals")
	return invoice


@frappe.whitelist()
def make_purchase_invoice_from_fuel(source_name):
	"""Create an ERPNext Purchase Invoice draft from a submitted Fuel Transaction."""
	fuel = frappe.get_doc("Logix Fuel Transaction", source_name)
	fuel.check_permission("read")
	if fuel.docstatus != 1:
		frappe.throw(_("Submit the Fuel Transaction before creating a Purchase Invoice."))
	if not frappe.has_permission("Purchase Invoice", ptype="create"):
		frappe.throw(_("You do not have permission to create a Purchase Invoice."), frappe.PermissionError)

	existing_invoice = frappe.db.exists(
		"Purchase Invoice", {"logix_fuel_transaction": fuel.name, "docstatus": ["<", 2]}
	)
	if existing_invoice:
		frappe.throw(_("Purchase Invoice {0} already exists for this Fuel Transaction.").format(existing_invoice))
	if not fuel.supplier:
		frappe.throw(_("Select a Fuel Supplier before creating a Purchase Invoice."))

	item_code = fuel.fuel_item or frappe.db.get_single_value("Logix Settings", "default_fuel_item")
	item = frappe.db.get_value(
		"Item",
		item_code,
		["disabled", "is_purchase_item", "item_name", "description", "stock_uom"],
		as_dict=True,
	) if item_code else None
	if not item or item.disabled or not item.is_purchase_item:
		frappe.throw(_("Set an enabled purchase Item as the Fuel Item or Default Fuel Item."))

	invoice = frappe.new_doc("Purchase Invoice")
	invoice.company = fuel.company
	invoice.currency = fuel.currency
	invoice.supplier = fuel.supplier
	invoice.supplier_name = frappe.db.get_value("Supplier", fuel.supplier, "supplier_name")
	invoice.posting_date = fuel.posting_date
	invoice.due_date = fuel.posting_date
	invoice.logix_fuel_transaction = fuel.name
	invoice.append(
		"items",
		{
			"item_code": item_code,
			"item_name": item.item_name,
			"description": _("{0}<br>Vehicle {1}, Trip {2}, Odometer {3} km").format(
				item.description or item.item_name, fuel.vehicle, fuel.trip, fuel.odometer
			),
			"uom": item.stock_uom,
			"conversion_factor": 1,
			"qty": flt(fuel.fuel_quantity),
			"rate": flt(fuel.rate),
			"expense_account": frappe.db.get_value(
				"Item Default", {"parent": item_code, "company": fuel.company}, "expense_account"
			)
			or frappe.db.get_value("Company", fuel.company, "default_expense_account"),
			"cost_center": frappe.db.get_value(
				"Item Default", {"parent": item_code, "company": fuel.company}, "buying_cost_center"
			)
			or frappe.db.get_value("Company", fuel.company, "cost_center"),
		},
	)
	invoice.run_method("calculate_taxes_and_totals")
	return invoice


@frappe.whitelist()
def create_job_from_estimation(estimation):
	est = frappe.get_doc("Logix Estimation", estimation)
	est.check_permission("read")
	frappe.db.sql("select name from `tabLogix Estimation` where name=%s for update", est.name)
	est.reload()
	_validate_estimation_for_job(est)
	job = make_job(est.name)
	job.insert()
	return job.name


@frappe.whitelist()
def regenerate_tracking_token(shipment):
	doc = frappe.get_doc("Logix Shipment", shipment)
	doc.check_permission("write")
	days = frappe.db.get_single_value("Logix Settings", "default_public_tracking_expiry_days") or 30
	doc.db_set({"tracking_token": secrets.token_urlsafe(32), "tracking_revoked": 0, "tracking_expires_on": add_days(now_datetime(), days)})
	return doc.tracking_token


@frappe.whitelist(allow_guest=True)
def public_tracking(token):
	if not isinstance(token, str) or len(token) < 32 or len(token) > 128:
		frappe.throw(_("Tracking link is invalid."), frappe.PermissionError)
	row = frappe.db.get_value(
		"Logix Shipment", {"tracking_token": token},
		["name", "status", "tracking_enabled", "tracking_revoked", "tracking_expires_on"], as_dict=True,
	)
	if not row or not row.tracking_enabled or row.tracking_revoked or not row.tracking_expires_on or row.tracking_expires_on < now_datetime():
		frappe.throw(_("Tracking link is invalid or expired."), frappe.PermissionError)
	milestones = frappe.get_all(
		"Logix Shipment Event", filters={"shipment": row.name},
		fields=["event_type", "event_time", "new_status"], order_by="event_time asc", limit_page_length=100,
	)
	return {"tracking_reference": token[-8:], "status": row.status, "milestones": milestones}
