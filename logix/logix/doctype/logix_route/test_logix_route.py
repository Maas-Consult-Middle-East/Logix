import frappe
from frappe.tests.utils import FrappeTestCase


class TestLogixRoute(FrappeTestCase):
	def test_name_uses_from_and_to_cities(self):
		suffix = frappe.generate_hash(length=6)
		from_city = frappe.get_doc(
			{"doctype": "Logix City", "city_name": f"Route Origin {suffix}"}
		).insert(ignore_permissions=True)
		to_city = frappe.get_doc(
			{"doctype": "Logix City", "city_name": f"Route Destination {suffix}"}
		).insert(ignore_permissions=True)

		route = frappe.get_doc(
			{
				"doctype": "Logix Route",
				"from_city": from_city.name,
				"to_city": to_city.name,
			}
		).insert(ignore_permissions=True)

		self.assertEqual(route.name, f"{from_city.name}-{to_city.name}")
