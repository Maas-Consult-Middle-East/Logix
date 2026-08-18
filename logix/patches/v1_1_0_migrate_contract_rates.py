import frappe
from frappe.utils import add_days, getdate, nowdate


def execute():
	"""Preserve legacy pricing and move active use to customer Contract Rates."""
	if not frappe.db.table_exists("Logix Contract Rate"):
		return
	card_map = {}
	if frappe.db.table_exists("Logix Transport Rate Card"):
		for card in frappe.get_all("Logix Transport Rate Card", fields=["*"]):
			legacy_reference = f"Legacy Transport Rate Card: {card.name}"
			existing = frappe.db.get_value("Logix Contract Rate", {"customer_contract_reference": legacy_reference}, "name")
			if existing:
				card_map[card.name] = existing
				continue
			requires_review = not bool(card.customer)
			notes = [legacy_reference]
			if card.round_trip_rate or card.return_trip_rate or card.excess_rate or card.cbm_pricing_enabled:
				notes.append("Legacy combined/return pricing was preserved as discrete rules and requires commercial verification.")
			contract = frappe.get_doc({"doctype":"Logix Contract Rate","contract_rate_name":card.name,"customer":card.customer,"currency":card.currency,"applicable_from":card.effective_from or nowdate(),"applicable_to":card.effective_to or "2099-12-31","disabled":1 if requires_review or card.disabled else 0,"requires_review":1 if requires_review else 0,"customer_contract_reference":legacy_reference,"notes":"\n".join(notes)})
			contract.append("contract_services", {"bill_by":"Route","from_city":card.from_city,"to_city":card.to_city,"vehicle_type":card.vehicle_type,"load_type":card.load_type,"route_rate":card.base_rate,"minimum_charge":card.minimum_freight,"extra_stop_rate":card.extra_stop_charge,"description":f"Migrated from {card.name}"})
			if card.excess_rate:
				contract.append("contract_services", {"bill_by":"Weight","from_city":card.from_city,"to_city":card.to_city,"vehicle_type":card.vehicle_type,"load_type":card.load_type,"rate_per_weight":card.excess_rate,"weight_uom":card.excess_weight_uom or "Kg","description":f"Legacy excess-weight rate; included threshold was {card.included_weight or 0}. Review before use."})
			if card.cbm_pricing_enabled and card.cbm_rate:
				contract.append("contract_services", {"bill_by":"CBM","from_city":card.from_city,"to_city":card.to_city,"vehicle_type":card.vehicle_type,"load_type":card.load_type,"rate_per_cbm":card.cbm_rate,"description":"Migrated legacy CBM rate."})
			contract.insert(ignore_permissions=True)
			card_map[card.name] = contract.name

	if not frappe.db.table_exists("Logix Estimation Item"):
		return
	default_company = frappe.db.get_single_value("Global Defaults", "default_company")
	default_currency = frappe.db.get_single_value("Global Defaults", "default_currency")
	validity_days = frappe.db.get_single_value("Logix Settings", "default_estimation_validity_days") or 30
	for row in frappe.get_all("Logix Estimation", fields=["name","creation","from_city","to_city","vehicle_type","load_type","base_weight","cbm","extra_stops","estimated_revenue","currency","rate_card"]):
		updates = {}
		estimation_date = getdate(row.creation) if row.creation else getdate(nowdate())
		for fieldname, value in (("estimation_date",estimation_date),("valid_until",add_days(estimation_date,validity_days)),("company",default_company),("currency",row.currency or default_currency),("contract_rate",card_map.get(row.rate_card))):
			if value and not frappe.db.get_value("Logix Estimation", row.name, fieldname): updates[fieldname] = value
		if updates: frappe.db.set_value("Logix Estimation", row.name, updates, update_modified=False)
		if frappe.db.exists("Logix Estimation Item", {"parent":row.name,"parenttype":"Logix Estimation"}): continue
		amount = row.estimated_revenue or 0
		frappe.get_doc({"doctype":"Logix Estimation Item","parent":row.name,"parenttype":"Logix Estimation","parentfield":"items","idx":1,"bill_by":"Manual","from_city":row.from_city,"to_city":row.to_city,"vehicle_type":row.vehicle_type,"load_type":row.load_type,"weight":row.base_weight,"cbm":row.cbm,"number_of_stops":row.extra_stops,"qty":1,"rate":amount,"amount":amount,"description":"Migrated legacy Estimation service","pricing_source":"Manual"}).db_insert()
		frappe.db.set_value("Logix Estimation", row.name, {"net_total":amount,"grand_total":amount,"estimated_selling_value_excluding_tax":amount}, update_modified=False)
	frappe.db.set_single_value("Logix Settings", "contract_rate_pricing_enabled", 1)
	frappe.db.set_single_value("Logix Settings", "rate_card_pricing_enabled", 0)
