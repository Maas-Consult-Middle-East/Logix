import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	can_view_cost = bool(frappe.db.get_single_value("Logix Settings", "estimation_cost_visibility")) and (
		frappe.session.user == "Administrator" or bool({"System Manager", "Logix Manager"}.intersection(frappe.get_roles()))
	)
	columns = [
		{"fieldname":"estimation","label":_("Estimation"),"fieldtype":"Link","options":"Logix Estimation","width":140},
		{"fieldname":"customer","label":_("Customer"),"fieldtype":"Link","options":"Customer","width":160},
		{"fieldname":"contract_rate","label":_("Contract Rate"),"fieldtype":"Link","options":"Logix Contract Rate","width":150},
		{"fieldname":"applicable_from","label":_("Applicable From"),"fieldtype":"Date","width":110},
		{"fieldname":"applicable_to","label":_("Applicable To"),"fieldtype":"Date","width":110},
		{"fieldname":"currency","label":_("Currency"),"fieldtype":"Link","options":"Currency","width":80},
		{"fieldname":"bill_by","label":_("Bill By"),"fieldtype":"Data","width":80},
		{"fieldname":"item_amount","label":_("Item Amount"),"fieldtype":"Currency","options":"currency","width":110},
		{"fieldname":"net_total","label":_("Net Total"),"fieldtype":"Currency","options":"currency","width":110},
		{"fieldname":"discount","label":_("Discount"),"fieldtype":"Currency","options":"currency","width":100},
		{"fieldname":"taxes","label":_("Taxes"),"fieldtype":"Currency","options":"currency","width":100},
		{"fieldname":"grand_total","label":_("Grand Total"),"fieldtype":"Currency","options":"currency","width":110},
		{"fieldname":"connected_job","label":_("Connected Job"),"fieldtype":"Data","width":150},
	]
	if can_view_cost:
		columns.extend([{"fieldname":"estimated_profit","label":_("Estimated Profit"),"fieldtype":"Currency","options":"currency","width":120},{"fieldname":"estimated_margin_percent","label":_("Estimated Margin %"),"fieldtype":"Percent","width":120}])
	parent_filters = {}
	for key in ("customer", "contract_rate"):
		if filters.get(key): parent_filters[key] = filters[key]
	if filters.get("from_date") and filters.get("to_date"):
		parent_filters["estimation_date"] = ["between", [filters.from_date, filters.to_date]]
	parents = frappe.get_list("Logix Estimation", filters=parent_filters, fields=["name","customer","contract_rate","currency","net_total","additional_discount_amount","total_taxes_and_charges","grand_total","estimated_profit","estimated_margin_percent"], order_by="estimation_date desc")
	data = []
	for parent in parents:
		validity = frappe.db.get_value("Logix Contract Rate", parent.contract_rate, ["applicable_from","applicable_to"], as_dict=True) if parent.contract_rate else frappe._dict()
		jobs = ", ".join(frappe.get_all("Logix Job", filters={"estimation":parent.name}, pluck="name"))
		items = frappe.get_all("Logix Estimation Item", filters={"parent":parent.name,"parenttype":"Logix Estimation"}, fields=["bill_by","amount"], order_by="idx") or [frappe._dict()]
		for item in items:
			row = {"estimation":parent.name,"customer":parent.customer,"contract_rate":parent.contract_rate,"applicable_from":validity.get("applicable_from"),"applicable_to":validity.get("applicable_to"),"currency":parent.currency,"bill_by":item.get("bill_by"),"item_amount":item.get("amount"),"net_total":parent.net_total,"discount":parent.additional_discount_amount,"taxes":parent.total_taxes_and_charges,"grand_total":parent.grand_total,"connected_job":jobs}
			if can_view_cost: row.update({"estimated_profit":parent.estimated_profit,"estimated_margin_percent":parent.estimated_margin_percent})
			data.append(row)
	return columns, data
