import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LogixTrip(Document):
	def validate(self):
		seen = set()
		for row in self.allocations:
			if flt(row.allocated_quantity) <= 0:
				frappe.throw(_("Allocated quantity must be greater than zero."))
			key = (row.shipment, row.shipment_leg)
			if key in seen:
				frappe.throw(_("A Shipment or leg may appear only once per Trip."))
			seen.add(key)
			shipment = frappe.db.get_value("Logix Shipment", row.shipment, ["job", "customer", "branch", "total_quantity"], as_dict=True)
			if not shipment or shipment.branch != self.branch:
				frappe.throw(_("Shipment {0} is unavailable in this Branch.").format(row.shipment))
			row.job, row.customer = shipment.job, shipment.customer
			allocated_elsewhere = frappe.db.sql(
				"""select coalesce(sum(a.allocated_quantity), 0) from `tabLogix Trip Shipment Allocation` a
				join `tabLogix Trip` t on t.name=a.parent
				where a.shipment=%s and a.status!='Removed' and t.docstatus<2 and t.name!=%s""",
				(row.shipment, self.name or ""),
			)[0][0]
			if flt(allocated_elsewhere) + flt(row.allocated_quantity) > flt(shipment.total_quantity):
				frappe.throw(_("Allocation exceeds remaining cargo for Shipment {0}.").format(row.shipment))

	def on_update(self):
		self._refresh_shipment_allocations()

	def on_cancel(self):
		self._refresh_shipment_allocations()

	def _refresh_shipment_allocations(self):
		for shipment in {row.shipment for row in self.allocations}:
			allocated = frappe.db.sql(
				"""select coalesce(sum(a.allocated_quantity), 0) from `tabLogix Trip Shipment Allocation` a
				join `tabLogix Trip` t on t.name=a.parent
				where a.shipment=%s and a.status!='Removed' and t.docstatus<2""",
				shipment,
			)[0][0]
			frappe.db.set_value("Logix Shipment", shipment, {"allocated_quantity": allocated})
