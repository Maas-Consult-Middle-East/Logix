import unittest

import frappe
from frappe.exceptions import ValidationError
from frappe.utils import add_days, nowdate

from logix.api import (
	make_job,
	make_purchase_invoice_from_fuel,
	make_pod,
	make_sales_invoice_from_pod,
	make_shipment,
	make_shipment_from_order,
	make_shipment_order,
	make_trip_from_plan,
	make_trip_from_shipment,
	make_trip_plan,
)


class TestLogixJob(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
		settings = frappe.get_single("Logix Settings")
		settings.manual_pricing_allowed = 1
		settings.estimation_cost_visibility = 1
		settings.save(ignore_permissions=True)
		if not frappe.db.exists("Branch", "Logix Test Branch"):
			frappe.get_doc({"doctype": "Branch", "branch": "Logix Test Branch"}).insert()
		if not frappe.db.exists("Customer Group", "Logix Test Group"):
			frappe.get_doc({"doctype": "Customer Group", "customer_group_name": "Logix Test Group", "is_group": 0}).insert()
		if not frappe.db.exists("Customer", "Logix Job Test Customer"):
			frappe.get_doc({"doctype": "Customer", "customer_name": "Logix Job Test Customer", "customer_group": "Logix Test Group", "customer_type": "Company"}).insert()
		for city in ("Logix Test Origin", "Logix Test Destination"):
			if not frappe.db.exists("Logix City", {"city_name": city}):
				frappe.get_doc({"doctype": "Logix City", "city_name": city}).insert(ignore_permissions=True)
		self.origin = frappe.db.get_value("Logix City", {"city_name": "Logix Test Origin"})
		self.destination = frappe.db.get_value("Logix City", {"city_name": "Logix Test Destination"})
		self.vehicle_type = self._master(
			"Logix Vehicle Type", {"vehicle_type_name": "Logix Job Test Vehicle Type"}
		)
		frappe.db.set_value(
			"Logix Vehicle Type",
			self.vehicle_type,
			{"weight_capacity_kg": 10000, "volume_capacity_cbm": 40},
		)
		self.load_type = self._master("Logix Load Type", {"load_type_name": "Logix Job Test Load Type"})

	def tearDown(self):
		frappe.db.rollback()

	def _job(self, estimation=None):
		return frappe.get_doc({
			"doctype": "Logix Job", "customer": "Logix Job Test Customer", "branch": "Logix Test Branch",
			"from_city": self.origin, "to_city": self.destination, "load_type": self.load_type,
			"estimation": estimation,
		})

	def _master(self, doctype, values):
		name = frappe.db.get_value(doctype, values, "name")
		if not name:
			name = frappe.get_doc({"doctype": doctype, **values}).insert(ignore_permissions=True).name
		return name

	def _estimation(self):
		return frappe.get_doc(
			{
				"doctype": "Logix Estimation",
				"customer": "Logix Job Test Customer",
				"company": frappe.db.get_single_value("Global Defaults", "default_company"),
				"branch": "Logix Test Branch",
				"status": "Draft",
				"estimation_date": nowdate(),
				"valid_until": add_days(nowdate(), 30),
				"currency": frappe.db.get_single_value("Global Defaults", "default_currency"),
				"estimated_direct_cost": 1750,
				"items": [{"bill_by":"Manual","description":"Transport service","qty":1,"rate":2500,"from_city":self.origin,"to_city":self.destination,"vehicle_type":self.vehicle_type,"load_type":self.load_type}],
			}
		).insert()

	def _shipment(self):
		job = self._job().insert()
		return frappe.get_doc(
			{
				"doctype": "Logix Shipment",
				"job": job.name,
				"customer": job.customer,
				"branch": job.branch,
				"load_type": job.load_type,
				"total_quantity": 12,
				"weight_kg": 750,
				"cbm": 4,
				"pallets": 3,
				"stops": [
					{"sequence": 1, "stop_type": "Pickup", "city": job.from_city},
					{"sequence": 2, "stop_type": "Delivery", "city": job.to_city},
				],
			}
		).insert()

	def test_estimation_requirement_switch(self):
		settings = frappe.get_single("Logix Settings")
		settings.disallow_job_without_estimation = 1
		settings.save()
		with self.assertRaises(ValidationError):
			self._job().insert()
		settings.disallow_job_without_estimation = 0
		settings.save()
		self.assertTrue(self._job().insert().name)

	def test_draft_estimation_is_not_eligible(self):
		estimation = self._estimation()
		with self.assertRaises(ValidationError):
			make_job(estimation.name)
		with self.assertRaises(ValidationError):
			self._job(estimation.name).insert()

	def test_expired_estimation_is_not_eligible(self):
		estimation = self._estimation()
		estimation.valid_until = add_days(nowdate(), -1)
		with self.assertRaises(ValidationError):
			estimation.save()

	def test_submitted_estimation_maps_to_job(self):
		estimation = self._estimation()
		estimation.status = "Accepted"
		estimation.submit()
		job = make_job(estimation.name)

		self.assertTrue(job.is_new())
		self.assertEqual(job.estimation, estimation.name)
		self.assertEqual(job.customer, estimation.customer)
		self.assertEqual(job.branch, estimation.branch)
		self.assertEqual(job.from_city, estimation.items[0].from_city)
		self.assertEqual(job.to_city, estimation.items[0].to_city)
		self.assertEqual(job.preferred_vehicle_type, estimation.items[0].vehicle_type)
		self.assertEqual(job.load_type, estimation.items[0].load_type)
		self.assertEqual(job.agreed_revenue, estimation.grand_total)
		self.assertEqual(job.estimated_cost, estimation.estimated_direct_cost)
		self.assertEqual(job.status, "Draft")

	def test_job_maps_to_shipment_order_and_shipment(self):
		job = self._job().insert()

		order = make_shipment_order(job.name)
		self.assertTrue(order.is_new())
		self.assertEqual(order.job, job.name)
		self.assertEqual(order.customer, job.customer)
		self.assertEqual(order.branch, job.branch)
		self.assertEqual(order.status, "Draft")

		shipment = make_shipment(job.name)
		self.assertTrue(shipment.is_new())
		self.assertEqual(shipment.job, job.name)
		self.assertEqual(shipment.customer, job.customer)
		self.assertEqual(shipment.branch, job.branch)
		self.assertEqual(shipment.load_type, job.load_type)
		self.assertEqual(
			[(row.sequence, row.stop_type, row.city) for row in shipment.stops],
			[(1, "Pickup", job.from_city), (2, "Delivery", job.to_city)],
		)

	def test_shipment_order_maps_to_shipment(self):
		job = self._job().insert()
		order = frappe.get_doc(
			{
				"doctype": "Logix Shipment Order",
				"job": job.name,
				"customer": job.customer,
				"branch": job.branch,
				"quantity": 12,
				"weight_kg": 750,
				"cbm": 4,
				"pallets": 3,
			}
		).insert()

		shipment = make_shipment_from_order(order.name)
		self.assertTrue(shipment.is_new())
		self.assertEqual(shipment.shipment_order, order.name)
		self.assertEqual(shipment.job, job.name)
		self.assertEqual(shipment.total_quantity, order.quantity)
		self.assertEqual(shipment.weight_kg, order.weight_kg)
		self.assertEqual(shipment.cbm, order.cbm)
		self.assertEqual(shipment.pallets, order.pallets)
		self.assertEqual(shipment.load_type, job.load_type)
		self.assertEqual(
			[(row.sequence, row.stop_type, row.city) for row in shipment.stops],
			[(1, "Pickup", job.from_city), (2, "Delivery", job.to_city)],
		)

	def test_shipment_maps_to_trip_plan_and_trip(self):
		shipment = self._shipment()

		for target in (make_trip_plan(shipment.name), make_trip_from_shipment(shipment.name)):
			self.assertTrue(target.is_new())
			self.assertEqual(target.branch, shipment.branch)
			self.assertEqual(len(target.allocations), 1)
			allocation = target.allocations[0]
			self.assertEqual(allocation.shipment, shipment.name)
			self.assertEqual(allocation.job, shipment.job)
			self.assertEqual(allocation.customer, shipment.customer)
			self.assertEqual(allocation.allocated_quantity, shipment.total_quantity)
			self.assertEqual(allocation.weight_kg, shipment.weight_kg)
			self.assertEqual(allocation.cbm, shipment.cbm)
			self.assertEqual(allocation.pallets, shipment.pallets)
			self.assertEqual(allocation.pickup_stop_sequence, 1)
			self.assertEqual(allocation.delivery_stop_sequence, 2)

	def test_trip_plan_maps_to_linked_trip(self):
		shipment = self._shipment()
		trip_plan = make_trip_plan(shipment.name)
		trip_plan.resource_mode = "Company Owned"
		trip_plan.insert()

		trip = make_trip_from_plan(trip_plan.name)
		self.assertTrue(trip.is_new())
		self.assertEqual(trip.trip_plan, trip_plan.name)
		self.assertEqual(trip.branch, trip_plan.branch)
		self.assertEqual(trip.resource_mode, trip_plan.resource_mode)
		self.assertEqual(len(trip.allocations), 1)
		self.assertEqual(trip.allocations[0].shipment, shipment.name)
		self.assertEqual(trip.allocations[0].allocated_quantity, shipment.total_quantity)

	def test_trip_maps_to_pod(self):
		shipment = self._shipment()
		trip = make_trip_from_shipment(shipment.name)
		trip.resource_mode = "Company Owned"
		trip.insert()

		pod = make_pod(trip.name, shipment=shipment.name)
		self.assertTrue(pod.is_new())
		self.assertEqual(pod.trip, trip.name)
		self.assertEqual(pod.shipment, shipment.name)
		self.assertEqual(pod.job, shipment.job)
		self.assertEqual(pod.customer, shipment.customer)
		self.assertEqual(pod.branch, trip.branch)
		self.assertEqual(pod.delivered_quantity, shipment.total_quantity)

		pod.received_by = "Logix Test Receiver"
		pod.proof_attachment = "/files/logix-test-pod.jpg"
		pod.insert().submit()
		self.assertEqual(pod.status, "Verified")
		with self.assertRaises(ValidationError):
			make_pod(trip.name, shipment=shipment.name)

	def test_verified_pod_maps_to_sales_invoice(self):
		shipment = self._shipment()
		job = frappe.get_doc("Logix Job", shipment.job)
		job.agreed_revenue = 2500
		job.save()
		trip = make_trip_from_shipment(shipment.name)
		trip.resource_mode = "Company Owned"
		trip.insert()
		pod = make_pod(trip.name, shipment=shipment.name)
		pod.received_by = "Logix Test Receiver"
		pod.proof_attachment = "/files/logix-test-pod.jpg"
		pod.insert().submit()

		item_code = "Logix Test Transport Service"
		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_code,
					"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
					"stock_uom": frappe.db.get_value("UOM", {"enabled": 1}),
					"is_stock_item": 0,
					"is_sales_item": 1,
				}
			).insert()
		settings = frappe.get_single("Logix Settings")
		settings.transport_service_item = item_code
		settings.save()

		invoice = make_sales_invoice_from_pod(pod.name)
		self.assertTrue(invoice.is_new())
		self.assertEqual(invoice.customer, pod.customer)
		self.assertEqual(invoice.logix_pod, pod.name)
		self.assertEqual(invoice.logix_trip, pod.trip)
		self.assertEqual(invoice.logix_shipment, pod.shipment)
		self.assertEqual(invoice.logix_job, pod.job)
		self.assertEqual(len(invoice.items), 1)
		self.assertEqual(invoice.items[0].item_code, item_code)
		self.assertEqual(invoice.items[0].qty, 1)
		self.assertEqual(invoice.items[0].rate, job.agreed_revenue)
		self.assertEqual(invoice.grand_total, job.agreed_revenue)

	def test_fuel_transaction_calculates_and_maps_to_purchase_invoice(self):
		shipment = self._shipment()
		vehicle = "LOGIX-TEST-FUEL-VEHICLE"
		if not frappe.db.exists("Vehicle", vehicle):
			frappe.get_doc(
				{
					"doctype": "Vehicle",
					"license_plate": vehicle,
					"make": "Logix Test",
					"model": "Fuel Test",
					"last_odometer": 1000,
					"fuel_type": "Diesel",
					"uom": "Litre",
				}
			).insert(ignore_permissions=True)
		driver = self._master("Driver", {"full_name": "Logix Fuel Test Driver", "status": "Active"})
		trip = make_trip_from_shipment(shipment.name)
		trip.resource_mode = "Company Owned"
		trip.vehicle = vehicle
		trip.driver = driver
		trip.insert()

		company = frappe.defaults.get_user_default("Company")
		settings = frappe.get_single("Logix Settings")
		settings.default_fuel_efficiency_kmpl = 8
		settings.abnormal_fuel_variance_percent = 20
		settings.save()

		fuel = frappe.get_doc(
			{
				"doctype": "Logix Fuel Transaction",
				"trip": trip.name,
				"branch": trip.branch,
				"vehicle": vehicle,
				"driver": driver,
				"company": company,
				"odometer": 1100,
				"fuel_quantity": 20,
				"rate": 2,
			}
		).insert()
		self.assertEqual(fuel.previous_odometer, 1000)
		self.assertEqual(fuel.distance_travelled, 100)
		self.assertEqual(fuel.total_cost, 40)
		self.assertEqual(fuel.actual_efficiency, 5)
		self.assertEqual(fuel.efficiency_variance_percent, 37.5)
		self.assertEqual(fuel.is_abnormal, 1)
		fuel.submit()
		self.assertEqual(frappe.db.get_value("Vehicle", vehicle, "last_odometer"), 1100)

		supplier = self._master(
			"Supplier",
			{
				"supplier_name": "Logix Fuel Test Supplier",
				"supplier_group": frappe.db.get_value("Supplier Group", {"is_group": 0}),
				"supplier_type": "Company",
			},
		)
		item_code = "Logix Test Fuel Item"
		if not frappe.db.exists("Item", item_code):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": item_code,
					"item_name": item_code,
					"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
					"stock_uom": frappe.db.get_value("UOM", {"enabled": 1}),
					"is_stock_item": 0,
					"is_purchase_item": 1,
				}
			).insert()
		fuel.db_set({"supplier": supplier, "fuel_item": item_code})

		invoice = make_purchase_invoice_from_fuel(fuel.name)
		self.assertTrue(invoice.is_new())
		self.assertEqual(invoice.supplier, supplier)
		self.assertEqual(invoice.logix_fuel_transaction, fuel.name)
		self.assertEqual(invoice.items[0].item_code, item_code)
		self.assertEqual(invoice.items[0].qty, 20)
		self.assertEqual(invoice.items[0].rate, 2)
		self.assertEqual(invoice.grand_total, 40)
