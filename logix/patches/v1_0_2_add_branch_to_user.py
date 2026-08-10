import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"User": [
				{
					"fieldname": "logix_branch",
					"label": "Branch",
					"fieldtype": "Link",
					"options": "Branch",
					"insert_after": "username",
					"in_standard_filter": 1,
					"description": "Default operational Branch for Logix",
				},
			]
		},
		update=True,
	)
