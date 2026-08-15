import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LogixPOD(Document):
	def validate(self):
		trip = frappe.db.get_value(
			"Logix Trip", self.trip, ["branch", "docstatus", "status"], as_dict=True
		)
		if not trip or trip.docstatus == 2 or trip.status == "Cancelled":
			frappe.throw(_("POD requires an active Trip."))

		shipment = frappe.db.get_value(
			"Logix Shipment", self.shipment, ["job", "customer", "branch"], as_dict=True
		)
		if not shipment or shipment.branch != trip.branch:
			frappe.throw(_("Shipment {0} is unavailable in this Trip's Branch.").format(self.shipment))

		allocations = frappe.get_all(
			"Logix Trip Shipment Allocation",
			filters={"parent": self.trip, "parenttype": "Logix Trip", "shipment": self.shipment},
			fields=["allocated_quantity", "status"],
		)
		allocated_quantity = sum(
			flt(row.allocated_quantity) for row in allocations if row.status != "Removed"
		)
		if not allocated_quantity:
			frappe.throw(_("Shipment {0} is not actively allocated to Trip {1}.").format(self.shipment, self.trip))

		if self.delivery_status != "Rejected" and flt(self.delivered_quantity) <= 0:
			frappe.throw(_("Delivered Quantity must be greater than zero."))
		if flt(self.delivered_quantity) > allocated_quantity:
			frappe.throw(_("Delivered Quantity cannot exceed the Trip's allocated quantity."))

		duplicate = frappe.db.exists(
			"Logix POD",
			{"trip": self.trip, "shipment": self.shipment, "docstatus": ["<", 2], "name": ["!=", self.name or ""]},
		)
		if duplicate:
			frappe.throw(_("An active POD already exists for this Trip and Shipment."))

		self.branch = trip.branch
		self.job = shipment.job
		self.customer = shipment.customer

	def before_submit(self):
		if not self.signature and not self.proof_attachment:
			frappe.throw(_("Add a receiver signature or proof attachment before submitting the POD."))
		self.status = "Verified"

	def before_cancel(self):
		self.status = "Cancelled"
