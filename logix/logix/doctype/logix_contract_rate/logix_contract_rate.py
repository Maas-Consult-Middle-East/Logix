import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class LogixContractRate(Document):
	def validate(self):
		if self.applicable_to and self.applicable_from and getdate(self.applicable_to) < getdate(self.applicable_from):
			frappe.throw(_("Applicable To cannot be before Applicable From."))
		if self.requires_review:
			self.disabled = 1
		if not self.customer and not self.requires_review:
			frappe.throw(_("A Contract Rate must belong to a Customer."))
		for service in self.contract_services:
			service.run_method("validate")

