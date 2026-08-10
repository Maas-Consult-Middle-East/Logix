import frappe
from frappe import _
from frappe.model.document import Document


class LogixHandover(Document):
	def before_insert(self):
		self.recorded_by = frappe.session.user

	def validate(self):
		from_shipment = frappe.db.get_value("Logix Shipment Leg", self.from_leg, "shipment")
		to_shipment = frappe.db.get_value("Logix Shipment Leg", self.to_leg, "shipment")
		if from_shipment != self.shipment or to_shipment != self.shipment:
			frappe.throw(_("Both handover legs must belong to the Shipment."))
