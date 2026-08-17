import frappe
from frappe import _
from frappe.model.document import Document


class LogixRoute(Document):
	def validate(self):
		if self.from_city == self.to_city:
			frappe.throw(_("From City and To City must be different."))
