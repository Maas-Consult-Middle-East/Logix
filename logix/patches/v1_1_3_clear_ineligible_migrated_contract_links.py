import frappe


def execute():
	"""Keep reviewed legacy references without making invalid contracts active."""
	for row in frappe.get_all("Logix Estimation", filters={"contract_rate":["is","set"]}, fields=["name","customer","contract_rate"]):
		contract = frappe.db.get_value("Logix Contract Rate", row.contract_rate, ["customer","disabled","requires_review"], as_dict=True)
		if not contract or contract.disabled or contract.requires_review or contract.customer != row.customer:
			frappe.db.set_value("Logix Estimation", row.name, "contract_rate", None, update_modified=False)
