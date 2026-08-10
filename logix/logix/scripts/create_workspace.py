import frappe


def create_logix_workspace():
    """Synchronize the standard workspace JSON into the current site."""
    from frappe.modules.import_file import import_file_by_path
    from frappe.modules.utils import get_module_path

    path = get_module_path("logix", "workspace", "logix", "logix.json")
    import_file_by_path(path, force=True, reset_permissions=True)
    return "Logix"
