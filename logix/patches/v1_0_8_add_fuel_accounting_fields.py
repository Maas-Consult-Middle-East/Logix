from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	create_custom_fields(
		{
			"Vehicle": [
				{
					"fieldname": "logix_expected_fuel_efficiency_kmpl",
					"label": "Expected Fuel Efficiency (km/L)",
					"fieldtype": "Float",
					"insert_after": "logix_vehicle_type",
				}
			],
			"Purchase Invoice": [
				{
					"fieldname": "logix_fuel_transaction",
					"label": "Logix Fuel Transaction",
					"fieldtype": "Link",
					"options": "Logix Fuel Transaction",
					"insert_after": "supplier",
					"read_only": 1,
					"in_standard_filter": 1,
					"unique": 0,
				}
			],
		},
		update=True,
	)
