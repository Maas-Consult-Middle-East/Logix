import frappe


def execute():
	"""Normalize legacy Data values before weight/CBM columns become numeric."""
	for fieldname in ("base_weight", "cbm"):
		if not frappe.db.has_column("Logix Estimation", fieldname):
			continue
		frappe.db.sql(
			f"""
			update `tabLogix Estimation`
			set `{fieldname}` = coalesce(
				regexp_substr(cast(`{fieldname}` as char), '-?[0-9]+([.][0-9]+)?'),
				'0'
			)
			where `{fieldname}` is null
				or trim(cast(`{fieldname}` as char)) = ''
				or cast(`{fieldname}` as char) not regexp '^-?[0-9]+([.][0-9]+)?$'
			"""
		)
