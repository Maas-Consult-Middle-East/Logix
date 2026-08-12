import frappe
from frappe.model.rename_doc import rename_doc


MASTER_NAME_FIELDS = {
	"Logix City": "city_name",
	"Logix Load Type": "load_type_name",
}


def execute():
	"""Rename legacy hash-named masters and update all links to their title values."""
	for doctype, fieldname in MASTER_NAME_FIELDS.items():
		for row in frappe.get_all(doctype, fields=["name", fieldname]):
			new_name = (row.get(fieldname) or "").strip()
			if not new_name or row.name == new_name:
				continue
			if frappe.db.exists(doctype, new_name):
				frappe.throw(
					f"Cannot rename {doctype} {row.name} to {new_name}: the target name already exists."
				)
			rename_doc(
				doctype,
				row.name,
				new_name,
				force=True,
				ignore_permissions=True,
				show_alert=False,
			)
