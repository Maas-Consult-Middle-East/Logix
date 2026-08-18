import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class LogixContractService(Document):
	def validate(self):
		if self.from_city and self.to_city and self.from_city == self.to_city:
			frappe.throw(_("Contract Service From and To must be different."))
		if self.bill_by == "Route" and (not self.from_city or not self.to_city or flt(self.route_rate) <= 0):
			frappe.throw(_("Route Contract Services require From, To, and a positive Route Rate."))
		if self.bill_by == "Weight" and (flt(self.rate_per_weight) <= 0 or not self.weight_uom):
			frappe.throw(_("Weight Contract Services require a positive Rate per Weight and Weight UOM."))
		if self.bill_by == "CBM" and flt(self.rate_per_cbm) <= 0:
			frappe.throw(_("CBM Contract Services require a positive Rate per CBM."))

