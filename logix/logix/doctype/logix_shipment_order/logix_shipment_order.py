import frappe
from frappe import _
from frappe.model.document import Document


class LogixShipmentOrder(Document):
	def validate(self):
		job = frappe.db.get_value("Logix Job", self.job, ["customer", "branch", "docstatus"], as_dict=True)
		if not job or job.docstatus == 2:
			frappe.throw(_("Shipment Order requires an active Job."))
		if self.customer != job.customer or self.branch != job.branch:
			frappe.throw(_("Customer and Branch must match the Job."))

	def before_cancel(self):
		if frappe.db.exists("Logix Shipment", {"shipment_order": self.name, "docstatus": ["<", 2]}):
			frappe.throw(_("Cancel dependent Shipments first."))
