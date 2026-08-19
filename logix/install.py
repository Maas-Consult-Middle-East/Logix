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
	after_migrate()


def after_migrate():
	"""Provision or repair the Workspace on both fresh installs and app upgrades."""
	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
	from logix.patches.v1_1_4_migrate_work_order_job_management_fields import WORK_ORDER_FIELDS

	before_install()
	create_custom_fields({"Work Order": WORK_ORDER_FIELDS}, update=True)
	create_logix_workspace()
	frappe.clear_cache()
