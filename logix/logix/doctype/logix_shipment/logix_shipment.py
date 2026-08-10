import secrets

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, now_datetime


class LogixShipment(Document):
	def before_insert(self):
		self._inherit_source()
		if self.tracking_enabled:
			self._new_tracking_token()

	def validate(self):
		if flt(self.total_quantity) <= 0:
			frappe.throw(_("Total Quantity must be greater than zero."))
		sequences = [row.sequence for row in self.stops]
		if len(sequences) != len(set(sequences)) or any(not sequence for sequence in sequences):
			frappe.throw(_("Shipment stop sequences must be unique positive values."))
		if not any(row.stop_type == "Pickup" for row in self.stops) or not any(row.stop_type == "Delivery" for row in self.stops):
			frappe.throw(_("A Shipment requires at least one pickup and one delivery stop."))
		self.remaining_quantity = flt(self.total_quantity) - flt(self.allocated_quantity)
		if self.remaining_quantity < 0:
			frappe.throw(_("Shipment cargo is over-allocated."))

	def before_cancel(self):
		if frappe.db.exists("Logix Trip Shipment Allocation", {"shipment": self.name, "docstatus": ["<", 2]}):
			frappe.throw(_("Remove active Trip allocations before cancelling the Shipment."))

	def _inherit_source(self):
		job = frappe.db.get_value("Logix Job", self.job, ["customer", "branch", "load_type", "docstatus"], as_dict=True)
		if not job or job.docstatus == 2:
			frappe.throw(_("Shipment requires an active Job."))
		self.customer = self.customer or job.customer
		self.branch = self.branch or job.branch
		self.load_type = self.load_type or job.load_type
		if self.shipment_order:
			order_job = frappe.db.get_value("Logix Shipment Order", self.shipment_order, "job")
			if order_job != self.job:
				frappe.throw(_("Shipment Order must belong to the same Job."))

	def _new_tracking_token(self):
		self.tracking_token = secrets.token_urlsafe(32)
		days = frappe.db.get_single_value("Logix Settings", "default_public_tracking_expiry_days") or 30
		self.tracking_expires_on = add_days(now_datetime(), days)
