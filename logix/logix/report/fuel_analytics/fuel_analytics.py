import frappe
from frappe import _

from logix.permissions import allowed_branches


def execute(filters=None):
	filters = frappe._dict(filters or {})
	columns = [
		{"label": _("Fuel Transaction"), "fieldname": "name", "fieldtype": "Link", "options": "Logix Fuel Transaction", "width": 175},
		{"label": _("Date"), "fieldname": "posting_date", "fieldtype": "Date", "width": 100},
		{"label": _("Branch"), "fieldname": "branch", "fieldtype": "Link", "options": "Branch", "width": 130},
		{"label": _("Vehicle"), "fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "width": 130},
		{"label": _("Driver"), "fieldname": "driver", "fieldtype": "Link", "options": "Driver", "width": 130},
		{"label": _("Trip"), "fieldname": "trip", "fieldtype": "Link", "options": "Logix Trip", "width": 150},
		{"label": _("Distance (km)"), "fieldname": "distance_travelled", "fieldtype": "Float", "width": 110},
		{"label": _("Fuel (L)"), "fieldname": "fuel_quantity", "fieldtype": "Float", "width": 95},
		{"label": _("Actual km/L"), "fieldname": "actual_efficiency", "fieldtype": "Float", "width": 105},
		{"label": _("Expected km/L"), "fieldname": "expected_efficiency", "fieldtype": "Float", "width": 115},
		{"label": _("Variance %"), "fieldname": "efficiency_variance_percent", "fieldtype": "Percent", "width": 100},
		{"label": _("Abnormal"), "fieldname": "is_abnormal", "fieldtype": "Check", "width": 85},
		{"label": _("Fuel Cost"), "fieldname": "total_cost", "fieldtype": "Currency", "options": "currency", "width": 115},
		{"label": _("Purchase Invoice"), "fieldname": "purchase_invoice", "fieldtype": "Link", "options": "Purchase Invoice", "width": 150},
	]
	conditions = ["docstatus = 1"]
	values = {}
	for fieldname, operator in (("from_date", ">="), ("to_date", "<=")):
		if filters.get(fieldname):
			conditions.append(f"posting_date {operator} %({fieldname})s")
			values[fieldname] = filters[fieldname]
	for fieldname in ("branch", "vehicle", "driver"):
		if filters.get(fieldname):
			conditions.append(f"`{fieldname}` = %({fieldname})s")
			values[fieldname] = filters[fieldname]
	if filters.get("abnormal_only"):
		conditions.append("is_abnormal = 1")
	branches = allowed_branches()
	if branches is not None:
		if not branches:
			return columns, []
		conditions.append("branch in %(allowed_branches)s")
		values["allowed_branches"] = branches
	data = frappe.db.sql(
		f"""
		select name, posting_date, branch, vehicle, driver, trip, distance_travelled,
			fuel_quantity, actual_efficiency, expected_efficiency, efficiency_variance_percent,
			is_abnormal, total_cost, currency, purchase_invoice
		from `tabLogix Fuel Transaction`
		where {' and '.join(conditions)}
		order by posting_date desc, posting_time desc
		""",
		values,
		as_dict=True,
	)
	return columns, data
