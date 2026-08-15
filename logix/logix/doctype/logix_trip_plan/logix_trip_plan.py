import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LogixTripPlan(Document):
	def validate(self):
		seen = set()
		for row in self.allocations:
			if flt(row.allocated_quantity) <= 0:
				frappe.throw(_("Allocated quantity must be greater than zero."))
			key = (row.shipment, row.shipment_leg)
			if key in seen:
				frappe.throw(_("A Shipment or leg may appear only once per Trip Plan."))
			seen.add(key)

			shipment = frappe.db.get_value(
				"Logix Shipment",
				row.shipment,
				["job", "customer", "branch", "total_quantity", "allocated_quantity"],
				as_dict=True,
			)
			if not shipment or shipment.branch != self.branch:
				frappe.throw(_("Shipment {0} is unavailable in this Branch.").format(row.shipment))

			remaining = flt(shipment.total_quantity) - flt(shipment.allocated_quantity)
			if flt(row.allocated_quantity) > remaining:
				frappe.throw(_("Planned allocation exceeds remaining cargo for Shipment {0}.").format(row.shipment))

			row.job = shipment.job
			row.customer = shipment.customer

	def before_cancel(self):
		if frappe.db.exists("Logix Trip", {"trip_plan": self.name, "docstatus": ["<", 2]}):
			frappe.throw(_("Cancel dependent Trips first."))
