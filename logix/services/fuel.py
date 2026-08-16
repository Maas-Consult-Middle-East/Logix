import frappe


def sync_fuel_purchase_invoice(doc, method=None):
	"""Keep the accounting reference on the originating fuel record synchronized."""
	if not getattr(doc, "logix_fuel_transaction", None):
		return
	if not frappe.db.exists("Logix Fuel Transaction", doc.logix_fuel_transaction):
		return
	frappe.db.set_value(
		"Logix Fuel Transaction",
		doc.logix_fuel_transaction,
		"purchase_invoice",
		None if doc.docstatus == 2 else doc.name,
		update_modified=False,
	)


def clear_fuel_purchase_invoice(doc, method=None):
	"""Clear a draft Purchase Invoice link when that draft is deleted."""
	if getattr(doc, "logix_fuel_transaction", None):
		frappe.db.set_value(
			"Logix Fuel Transaction",
			doc.logix_fuel_transaction,
			"purchase_invoice",
			None,
			update_modified=False,
		)
