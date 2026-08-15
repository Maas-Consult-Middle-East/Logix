from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Sales Invoice": [
				{
					"fieldname": "logix_pod",
					"label": "Logix POD",
					"fieldtype": "Link",
					"options": "Logix POD",
					"insert_after": "customer",
					"read_only": 1,
					"in_standard_filter": 1,
				},
				{
					"fieldname": "logix_trip",
					"label": "Logix Trip",
					"fieldtype": "Link",
					"options": "Logix Trip",
					"insert_after": "logix_pod",
					"read_only": 1,
				},
				{
					"fieldname": "logix_shipment",
					"label": "Logix Shipment",
					"fieldtype": "Link",
					"options": "Logix Shipment",
					"insert_after": "logix_trip",
					"read_only": 1,
				},
				{
					"fieldname": "logix_job",
					"label": "Logix Job",
					"fieldtype": "Link",
					"options": "Logix Job",
					"insert_after": "logix_shipment",
					"read_only": 1,
				},
			]
		},
		update=True,
	)
