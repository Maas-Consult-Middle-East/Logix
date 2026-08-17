import frappe
from frappe.model.rename_doc import rename_doc


def execute():
	for route in frappe.get_all("Logix Route", fields=["name", "from_city", "to_city"]):
		if not route.from_city or not route.to_city:
			continue

		new_name = f"{route.from_city}-{route.to_city}"
		if route.name == new_name or frappe.db.exists("Logix Route", new_name):
			continue

		rename_doc(
			"Logix Route",
			route.name,
			new_name,
			force=True,
			ignore_permissions=True,
			show_alert=False,
		)
