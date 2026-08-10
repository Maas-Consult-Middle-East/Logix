import unittest

import frappe
from frappe.exceptions import ValidationError


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

	def tearDown(self):
		frappe.db.rollback()

	def _job(self, estimation=None):
		return frappe.get_doc({
			"doctype": "Logix Job", "customer": "Logix Job Test Customer", "branch": "Logix Test Branch",
			"from_city": self.origin, "to_city": self.destination, "estimation": estimation,
		})

	def test_estimation_requirement_switch(self):
		settings = frappe.get_single("Logix Settings")
		settings.disallow_job_without_estimation = 1
		settings.save()
		with self.assertRaises(ValidationError):
			self._job().insert()
		settings.disallow_job_without_estimation = 0
		settings.save()
		self.assertTrue(self._job().insert().name)
