import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, nowdate


class LogixJob(Document):
	def before_insert(self):
		self._inherit_customer_defaults()

	def validate(self):
		self._validate_estimation_requirement()
		self._validate_controlled_closure()
		self.actual_profit = flt(self.agreed_revenue) - flt(self.actual_cost)
		self.actual_margin_percent = self.actual_profit / flt(self.agreed_revenue) * 100 if self.agreed_revenue else 0

	def after_insert(self):
		if self.estimation:
			frappe.db.set_value("Logix Estimation", self.estimation, {"status": "Accepted", "downstream_job": self.name})

	def before_cancel(self):
		for doctype, field in (("Logix Shipment Order", "job"), ("Logix Shipment", "job")):
			if frappe.db.exists(doctype, {field: self.name, "docstatus": ["<", 2]}):
				frappe.throw(_("Cancel dependent {0} records first.").format(doctype))

	def _validate_estimation_requirement(self):
		settings = frappe.get_single("Logix Settings")
		if settings.disallow_job_without_estimation and not self.estimation:
			frappe.throw(_("An eligible Estimation is required for this Job."))
		if self.estimation:
			# Serialize Job creation for this Estimation so concurrent inserts cannot
			# both pass the duplicate check. The row lock lasts to commit/rollback.
			frappe.db.sql("select name from `tabLogix Estimation` where name=%s for update", self.estimation)
			estimation = frappe.db.get_value(
				"Logix Estimation",
				self.estimation,
				["customer", "docstatus", "status", "valid_until"],
				as_dict=True,
			)
			if (
				not estimation
				or estimation.customer != self.customer
				or estimation.docstatus != 1
				or estimation.status != "Accepted"
			):
				frappe.throw(_("The selected Estimation is not eligible for this Job."))
			if estimation.valid_until and getdate(estimation.valid_until) < getdate(nowdate()):
				frappe.throw(_("A Job cannot be created from an expired Estimation."))
			duplicate = self.is_new() and frappe.db.get_value(
				"Logix Job", {"estimation": self.estimation}, "name"
			)
			if duplicate:
				frappe.throw(_("Job {0} has already been created from this Estimation.").format(duplicate))

	def _validate_controlled_closure(self):
		if self.status in ("Stopped", "Partially Completed", "Cancelled with Executed Work Retained") and not self.closure_reason:
			frappe.throw(_("A closure reason is required for this Job outcome."))

	def _inherit_customer_defaults(self):
		if not self.customer:
			return
		defaults = frappe.db.get_value("Customer", self.customer, ["logix_default_branch", "logix_default_load_type"], as_dict=True)
		if defaults:
			self.branch = self.branch or defaults.logix_default_branch
			self.load_type = self.load_type or defaults.logix_default_load_type
