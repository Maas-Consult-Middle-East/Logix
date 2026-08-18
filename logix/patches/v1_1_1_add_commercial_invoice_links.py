from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields({"Sales Invoice": [
		{"fieldname":"logix_estimation","label":"Logix Estimation","fieldtype":"Link","options":"Logix Estimation","insert_after":"logix_job","read_only":1,"in_standard_filter":1},
		{"fieldname":"logix_contract_rate","label":"Logix Contract Rate","fieldtype":"Link","options":"Logix Contract Rate","insert_after":"logix_estimation","read_only":1},
	]}, update=True)
