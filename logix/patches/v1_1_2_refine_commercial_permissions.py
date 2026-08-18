import frappe
from frappe.permissions import add_permission, update_permission_property


def execute():
	"""Preserve customized permissions while adding explicit cost-level access."""
	for role, write in (("System Manager", 1), ("Logix Manager", 1), ("Logix Finance User", 0)):
		if not frappe.db.exists("Custom DocPerm", {"parent":"Logix Estimation","role":role,"permlevel":1,"if_owner":0}):
			add_permission("Logix Estimation", role, permlevel=1, ptype="read")
		update_permission_property("Logix Estimation", role, 1, "read", 1)
		update_permission_property("Logix Estimation", role, 1, "write", write)
	frappe.clear_cache(doctype="Logix Estimation")
