import frappe

from logix.logix.scripts.create_workspace import create_logix_workspace


LOGIX_ROLES = (
	"Logix Manager",
	"Logix Branch Manager",
	"Logix Dispatcher",
	"Logix Operations User",
	"Logix Estimator",
	"Logix Driver",
	"Logix Finance User",
	"Logix Storage User",
	"Logix Read Only",
)


def before_install():
	"""Create role dependencies needed by the standard Workspace during schema sync."""
	for role_name in LOGIX_ROLES:
		if not frappe.db.exists("Role", role_name):
			frappe.get_doc({"doctype": "Role", "role_name": role_name}).insert(ignore_permissions=True)


def after_install():
	"""Ensure every fresh Logix installation receives the populated Desk workspace."""
	create_logix_workspace()
	frappe.clear_cache()
