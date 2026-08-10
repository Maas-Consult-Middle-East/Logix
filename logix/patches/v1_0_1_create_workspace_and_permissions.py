from __future__ import unicode_literals
import frappe


def execute():
    # Create a simple Workspace for Logix if missing
    if not frappe.db.exists("Workspace", "Logix"):
        try:
            ws = frappe.get_doc({
                "doctype": "Workspace",
                "module": "Logix",
                "title": "Logix",
            })
            ws.insert(ignore_permissions=True)
            frappe.db.commit()
        except Exception:
            frappe.log_error(frappe.get_traceback(), "logix: create workspace")

    # Ensure the Logix Manager role exists (idempotent)
    if not frappe.db.exists("Role", "Logix Manager"):
        frappe.get_doc({"doctype": "Role", "role_name": "Logix Manager"}).insert(ignore_permissions=True)
