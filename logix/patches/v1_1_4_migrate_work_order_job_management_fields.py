import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


WORK_ORDER_FIELDS = [
	{
		"fieldname": "custom_job_management_tab",
		"label": "Job Management",
		"fieldtype": "Tab Break",
		"insert_after": "required_items",
	},
	{
		"fieldname": "custom_production_section",
		"label": "Production",
		"fieldtype": "Section Break",
		"insert_after": "custom_job_management_tab",
	},
	{
		"fieldname": "custom_production_status",
		"label": "Production Status",
		"fieldtype": "Select",
		"options": "\nIn\nOut",
		"insert_after": "custom_production_section",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_is_reprint",
		"label": "Is Reprint",
		"fieldtype": "Check",
		"default": "0",
		"insert_after": "custom_production_status",
		"allow_on_submit": 1,
	},
	{"fieldname": "custom_production_column", "fieldtype": "Column Break", "insert_after": "custom_is_reprint"},
	{
		"fieldname": "custom_production_start_date",
		"label": "Production Start Date",
		"fieldtype": "Date",
		"insert_after": "custom_production_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{
		"fieldname": "custom_production_end_column",
		"fieldtype": "Column Break",
		"insert_after": "custom_production_start_date",
	},
	{
		"fieldname": "custom_production_end_date",
		"label": "Production End Date",
		"fieldtype": "Date",
		"insert_after": "custom_production_end_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{
		"fieldname": "custom_production_delay_column",
		"fieldtype": "Column Break",
		"insert_after": "custom_production_end_date",
	},
	{
		"fieldname": "custom_production_delay_reason",
		"label": "Production Delay Reason",
		"fieldtype": "Small Text",
		"insert_after": "custom_production_delay_column",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_reprint_section",
		"label": "Reprint",
		"fieldtype": "Section Break",
		"insert_after": "custom_production_delay_reason",
	},
	{
		"fieldname": "custom_reprint_status",
		"label": "Reprint Status",
		"fieldtype": "Select",
		"options": "\nIn\nOut",
		"insert_after": "custom_reprint_section",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{"fieldname": "custom_reprint_start_column", "fieldtype": "Column Break", "insert_after": "custom_reprint_status"},
	{
		"fieldname": "custom_reprint_start_date",
		"label": "Reprint Start Date",
		"fieldtype": "Date",
		"insert_after": "custom_reprint_start_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{"fieldname": "custom_reprint_end_column", "fieldtype": "Column Break", "insert_after": "custom_reprint_start_date"},
	{
		"fieldname": "custom_reprint_end_date",
		"label": "Reprint End Date",
		"fieldtype": "Date",
		"insert_after": "custom_reprint_end_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{
		"fieldname": "custom_binding_jobs_section",
		"label": "Binding Jobs",
		"fieldtype": "Section Break",
		"insert_after": "custom_reprint_end_date",
		"depends_on": 'eval:doc.custom_production_status=="Out"',
	},
	{
		"fieldname": "custom_binding_status",
		"label": "Binding Status",
		"fieldtype": "Select",
		"options": "\nIn\nOut",
		"insert_after": "custom_binding_jobs_section",
		"allow_on_submit": 1,
	},
	{"fieldname": "custom_packing_start_column", "fieldtype": "Column Break", "insert_after": "custom_binding_status"},
	{
		"fieldname": "custom_packing_start_date",
		"label": "Packing Start Date",
		"fieldtype": "Date",
		"insert_after": "custom_packing_start_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{"fieldname": "custom_packing_end_column", "fieldtype": "Column Break", "insert_after": "custom_packing_start_date"},
	{
		"fieldname": "custom_packing_end_date",
		"label": "Packing End Date",
		"fieldtype": "Date",
		"insert_after": "custom_packing_end_column",
		"allow_on_submit": 1,
		"read_only": 1,
	},
	{"fieldname": "custom_packing_delay_column", "fieldtype": "Column Break", "insert_after": "custom_packing_end_date"},
	{
		"fieldname": "custom_packing_delay_reason",
		"label": "Packing Delay Reason",
		"fieldtype": "Small Text",
		"insert_after": "custom_packing_delay_column",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_store_section",
		"label": "Store",
		"fieldtype": "Section Break",
		"insert_after": "custom_packing_delay_reason",
	},
	{
		"fieldname": "custom_store_status",
		"label": "Store Status",
		"fieldtype": "Select",
		"options": "\nIn\nOut",
		"insert_after": "custom_store_section",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{"fieldname": "custom_store_request_column", "fieldtype": "Column Break", "insert_after": "custom_store_status"},
	{
		"fieldname": "custom_store_request_date",
		"label": "Store Request Date",
		"fieldtype": "Date",
		"insert_after": "custom_store_request_column",
		"allow_on_submit": 1,
	},
	{"fieldname": "custom_packing_issue_column", "fieldtype": "Column Break", "insert_after": "custom_store_request_date"},
	{
		"fieldname": "custom_packing_issue_date",
		"label": "Packing Issue Date",
		"fieldtype": "Date",
		"insert_after": "custom_packing_issue_column",
		"allow_on_submit": 1,
	},
	{"fieldname": "custom_store_delay_column", "fieldtype": "Column Break", "insert_after": "custom_packing_issue_date"},
	{
		"fieldname": "custom_store_delay_reason",
		"label": "Store Delay Reason",
		"fieldtype": "Small Text",
		"insert_after": "custom_store_delay_column",
	},
	{
		"fieldname": "custom_delivery_section",
		"label": "Delivery",
		"fieldtype": "Section Break",
		"insert_after": "custom_store_delay_reason",
	},
	{
		"fieldname": "custom_status_for_delivery",
		"label": "Status for Delivery",
		"fieldtype": "Select",
		"options": "\nIn\nOut",
		"insert_after": "custom_delivery_section",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_delivery_quantities_column",
		"fieldtype": "Column Break",
		"insert_after": "custom_status_for_delivery",
	},
	{
		"fieldname": "custom_production_qty",
		"label": "Production Qty",
		"fieldtype": "Data",
		"insert_after": "custom_delivery_quantities_column",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_delivery_qty",
		"label": "Delivery Qty",
		"fieldtype": "Data",
		"insert_after": "custom_production_qty",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{
		"fieldname": "custom_balance",
		"label": "Balance",
		"fieldtype": "Data",
		"insert_after": "custom_delivery_qty",
		"allow_on_submit": 1,
		"translatable": 1,
	},
	{"fieldname": "custom_delivery_delay_column", "fieldtype": "Column Break", "insert_after": "custom_balance"},
	{
		"fieldname": "custom_delivery_delay_reason",
		"label": "Delivery Delay Reason",
		"fieldtype": "Small Text",
		"insert_after": "custom_delivery_delay_column",
		"allow_on_submit": 1,
		"translatable": 1,
	},
]


LEGACY_VALUE_FIELDS = (
	"production_status",
	"is_reprint",
	"production_start_date",
	"production_end_date",
	"production_delay_reason",
	"reprint_status",
	"reprint_start_date",
	"reprint_end_date",
	"binding_status",
	"packing_start_date",
	"packing_end_date",
	"packing_delay_reason",
	"store_status",
	"store_request_date",
	"packing_issue_date",
	"store_delay_reason",
	"status_for_delivery",
	"production_qty",
	"delivery_qty",
	"balance",
	"delivery_delay_reason",
)


def execute():
	create_custom_fields({"Work Order": WORK_ORDER_FIELDS}, update=True)

	# Frappe keeps removed DocType columns, so copy the existing values before a
	# future database cleanup can remove those legacy columns.
	work_order = frappe.qb.DocType("Work Order")
	for legacy_field in LEGACY_VALUE_FIELDS:
		custom_field = f"custom_{legacy_field}"
		if frappe.db.has_column("Work Order", legacy_field) and frappe.db.has_column("Work Order", custom_field):
			legacy_column = work_order[legacy_field]
			custom_column = work_order[custom_field]
			(
				frappe.qb.update(work_order)
				.set(custom_column, legacy_column)
				.where(legacy_column.isnotnull())
			).run()
