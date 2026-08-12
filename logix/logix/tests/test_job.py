import unittest

import frappe
from frappe.exceptions import ValidationError

from logix.api import make_job


class TestLogixJob(unittest.TestCase):
	def setUp(self):
		frappe.set_user("Administrator")
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
		self.load_type = self._master("Logix Load Type", {"load_type_name": "Logix Job Test Load Type"})

	def tearDown(self):
		frappe.db.rollback()

	def _job(self, estimation=None):
		return frappe.get_doc({
			"doctype": "Logix Job", "customer": "Logix Job Test Customer", "branch": "Logix Test Branch",
			"from_city": self.origin, "to_city": self.destination, "estimation": estimation,
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
				"branch": "Logix Test Branch",
				"status": "Draft",
				"estimated_revenue": 2500,
				"estimated_direct_cost": 1750,
				"from_city": self.origin,
				"to_city": self.destination,
				"vehicle_type": self.vehicle_type,
				"load_type": self.load_type,
				"base_weight": 1000,
				"pricing_source": "Manual",
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

	def test_submitted_estimation_maps_to_job(self):
		estimation = self._estimation().submit()
		job = make_job(estimation.name)

		self.assertTrue(job.is_new())
		self.assertEqual(job.estimation, estimation.name)
		self.assertEqual(job.customer, estimation.customer)
		self.assertEqual(job.branch, estimation.branch)
		self.assertEqual(job.from_city, estimation.from_city)
		self.assertEqual(job.to_city, estimation.to_city)
		self.assertEqual(job.preferred_vehicle_type, estimation.vehicle_type)
		self.assertEqual(job.load_type, estimation.load_type)
		self.assertEqual(job.agreed_revenue, estimation.estimated_revenue)
		self.assertEqual(job.estimated_cost, estimation.estimated_direct_cost)
		self.assertEqual(job.status, "Draft")
