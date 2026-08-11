import frappe


def create_logix_workspace():
    """Synchronize and verify the app's filtered Logix Workspace fixture."""
    from frappe.utils.fixtures import sync_fixtures

    sync_fixtures("logix")

    if not frappe.db.exists("Workspace", "Logix"):
        frappe.throw("Logix Workspace fixture could not be installed.")

    workspace = frappe.get_doc("Workspace", "Logix")
    if "System Manager" not in {row.role for row in workspace.roles}:
        workspace.append("roles", {"role": "System Manager"})
        workspace.save(ignore_permissions=True)

    return "Logix"
