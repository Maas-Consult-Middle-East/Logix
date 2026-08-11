import frappe


def create_logix_workspace():
    """Synchronize the app's filtered fixtures, including the Logix Workspace."""
    from frappe.utils.fixtures import sync_fixtures

    sync_fixtures("logix")
    return "Logix"
