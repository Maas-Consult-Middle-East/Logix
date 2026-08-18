import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class LogixTransportRateCard(Document):
	def before_insert(self):
		frappe.throw(_("Transport Rate Card is archived. Create a customer Contract Rate instead."))

	def validate(self):
		if self.from_city == self.to_city:
			frappe.throw(_("From City and To City must be different."))
		if self.effective_to and getdate(self.effective_to) < getdate(self.effective_from):
			frappe.throw(_("Effective To cannot be before Effective From."))
