from __future__ import annotations

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, flt, getdate, now, nowdate

from logix.services.contract_pricing import calculate_contract_price, validate_contract_rate


COMMERCIAL_MANAGER_ROLES = {"Administrator", "System Manager", "Logix Manager"}
COMMERCIAL_FIELDS = ("customer", "company", "branch", "estimation_date", "valid_until", "currency", "contract_rate", "items", "taxes_and_charges_template", "taxes", "apply_discount_on", "additional_discount_percentage", "additional_discount_amount", "net_total", "total_taxes_and_charges", "grand_total")


def _is_commercial_manager(user=None):
	user = user or frappe.session.user
	return user == "Administrator" or bool(COMMERCIAL_MANAGER_ROLES.intersection(frappe.get_roles(user)))


class LogixEstimation(Document):
	def onload(self):
		if frappe.db.get_single_value("Logix Settings", "estimation_cost_visibility") and _is_commercial_manager():
			self.set_onload("can_view_costing", True)
			return
		self.set_onload("can_view_costing", False)
		for fieldname in ("estimated_direct_cost", "estimated_selling_value_excluding_tax", "estimated_profit", "estimated_margin_percent", "pricing_variance", "rate_override_information", "cost_breakdown", "costing_notes"):
			self.set(fieldname, [] if fieldname == "cost_breakdown" else None)

	def before_insert(self):
		self.estimation_date = self.estimation_date or nowdate()
		if not self.valid_until:
			days = frappe.db.get_single_value("Logix Settings", "default_estimation_validity_days") or 30
			self.valid_until = add_days(self.estimation_date, int(days))
		self.company = self.company or frappe.db.get_single_value("Global Defaults", "default_company")
		self.currency = self.currency or frappe.db.get_single_value("Global Defaults", "default_currency")

	def validate(self):
		self._preserve_restricted_costing()
		self._validate_dates_and_status()
		if self.contract_rate:
			validate_contract_rate(self.contract_rate, self.customer, self.currency, self.estimation_date)
		self._validate_and_price_items()
		self._calculate_totals()
		self._calculate_profitability()
		self._validate_downstream_lock()

	def _preserve_restricted_costing(self):
		if frappe.db.get_single_value("Logix Settings", "estimation_cost_visibility") and _is_commercial_manager():
			return
		before = self.get_doc_before_save()
		if before:
			for fieldname in ("estimated_direct_cost", "cost_breakdown", "costing_notes"):
				self.set(fieldname, before.get(fieldname))
		elif self.cost_breakdown or flt(self.estimated_direct_cost):
			frappe.throw(_("You are not authorized to set Estimation costing information."))

	def on_submit(self):
		if self.status == "Draft":
			self.db_set("status", "Submitted", update_modified=False)

	def _validate_dates_and_status(self):
		if getdate(self.valid_until) < getdate(self.estimation_date):
			frappe.throw(_("Valid Until cannot be before Estimation Date."))
		if self.status not in {"Draft", "Submitted", "Sent to Customer", "Accepted", "Rejected"}:
			frappe.throw(_("Invalid commercial status: {0}").format(self.status))

	def _validate_and_price_items(self):
		if not self.items:
			frappe.throw(_("Add at least one Estimation Item."))
		overrides = []
		for row in self.items:
			if row.from_city and row.to_city and row.from_city == row.to_city:
				frappe.throw(_("Row {0}: From and To must be different.").format(row.idx))
			if row.bill_by == "Manual":
				self._price_manual_item(row)
				continue
			if not frappe.db.get_single_value("Logix Settings", "contract_rate_pricing_enabled"):
				frappe.throw(_("Contract Rate pricing is disabled in Logix Settings."))
			result = calculate_contract_price(customer=self.customer, contract_rate=self.contract_rate, estimation_date=self.estimation_date, currency=self.currency, bill_by=row.bill_by, from_city=row.from_city, to_city=row.to_city, vehicle_type=row.vehicle_type, load_type=row.load_type, weight=row.weight, weight_uom=row.weight_uom, cbm=row.cbm, number_of_stops=row.number_of_stops)
			row.contract_service = result.matched_contract_service
			row.suggested_rate = result.rate
			row.needs_repricing = 0
			if row.manual_rate_override:
				self._validate_override(row)
				row.pricing_source = "Override"
				row.amount = self._override_amount(row, result.additional_amount)
				overrides.append(_("Row {0}: {1} by {2}").format(row.idx, row.override_reason, row.override_user))
			else:
				if row.rate and row.pricing_source == "Contract Rate" and abs(flt(row.rate) - result.rate) > 0.000001:
					frappe.throw(_("Row {0}: mark the changed Contract Rate as an override and provide a reason.").format(row.idx))
				row.rate, row.amount, row.pricing_source = result.rate, result.final_amount, "Contract Rate"
		self.rate_override_information = "\n".join(overrides)
		self.pricing_variance = sum(flt(row.amount) - self._suggested_amount(row) for row in self.items if row.pricing_source == "Override")

	def _price_manual_item(self, row):
		settings, roles = frappe.get_single("Logix Settings"), set(frappe.get_roles())
		if not settings.manual_pricing_allowed or not (_is_commercial_manager() or "Logix Estimator" in roles):
			frappe.throw(_("Row {0}: you are not authorized to use Manual pricing.").format(row.idx))
		row.qty = flt(row.qty) or 1
		if row.qty <= 0 or flt(row.rate) < 0:
			frappe.throw(_("Row {0}: Manual quantity must be positive and rate cannot be negative.").format(row.idx))
		if not row.description:
			frappe.throw(_("Row {0}: Description is required for Manual billing.").format(row.idx))
		row.amount, row.pricing_source, row.contract_service = row.qty * flt(row.rate), "Manual", None
		row.suggested_rate, row.manual_rate_override = 0, 0

	def _validate_override(self, row):
		if not _is_commercial_manager():
			frappe.throw(_("Row {0}: only an authorized Commercial Manager may override a Contract Rate.").format(row.idx))
		if not row.override_reason:
			frappe.throw(_("Row {0}: Override Reason is required.").format(row.idx))
		if flt(row.rate) < 0:
			frappe.throw(_("Row {0}: Override Rate cannot be negative.").format(row.idx))
		row.override_user, row.override_timestamp = frappe.session.user, now()

	def _override_amount(self, row, additional):
		if row.bill_by == "Weight": return flt(row.weight) * flt(row.rate)
		if row.bill_by == "CBM": return flt(row.cbm) * flt(row.rate)
		return flt(row.rate) + flt(additional)

	def _suggested_amount(self, row):
		if row.bill_by == "Weight": return flt(row.weight) * flt(row.suggested_rate)
		if row.bill_by == "CBM": return flt(row.cbm) * flt(row.suggested_rate)
		return flt(row.suggested_rate)

	def _calculate_totals(self):
		self.net_total = sum(flt(row.amount) for row in self.items)
		basis, percentage, entered_amount = self.apply_discount_on or "Net Total", flt(self.additional_discount_percentage), flt(self.additional_discount_amount)
		if percentage < 0 or percentage > 100 or entered_amount < 0:
			frappe.throw(_("Additional discount must be between 0 and 100 percent and cannot be negative."))
		if (percentage or entered_amount) and not _is_commercial_manager():
			frappe.throw(_("Only an authorized Commercial Manager may apply an additional discount."))
		use_percentage = bool(percentage)
		before = self.get_doc_before_save()
		if before:
			percentage_changed = percentage != flt(before.additional_discount_percentage)
			amount_changed = entered_amount != flt(before.additional_discount_amount)
			if amount_changed and not percentage_changed:
				use_percentage = False
		if basis == "Net Total":
			discount_base = flt(self.net_total)
			discount = discount_base * percentage / 100 if use_percentage else entered_amount
			if discount > discount_base: frappe.throw(_("Additional Discount Amount cannot exceed Net Total."))
			self.additional_discount_amount = discount
			self.additional_discount_percentage = discount / discount_base * 100 if discount_base else 0
			taxable_net = discount_base - discount
			self.total_taxes_and_charges = self._calculate_taxes(taxable_net)
			self.grand_total = taxable_net + self.total_taxes_and_charges
			self.estimated_selling_value_excluding_tax = taxable_net
		elif basis == "Grand Total":
			taxes = self._calculate_taxes(flt(self.net_total))
			pre_discount_total = flt(self.net_total) + taxes
			discount = pre_discount_total * percentage / 100 if use_percentage else entered_amount
			if discount > pre_discount_total: frappe.throw(_("Additional Discount Amount cannot exceed Grand Total."))
			self.additional_discount_amount = discount
			self.additional_discount_percentage = discount / pre_discount_total * 100 if pre_discount_total else 0
			self.total_taxes_and_charges, self.grand_total = taxes, pre_discount_total - discount
			self.estimated_selling_value_excluding_tax = flt(self.net_total) * (1 - discount / pre_discount_total) if pre_discount_total else 0
		else:
			frappe.throw(_("Apply Additional Discount On must be Net Total or Grand Total."))

	def _calculate_taxes(self, taxable_net):
		running_total, previous_amount, previous_total = taxable_net, 0.0, taxable_net
		for row in self.taxes:
			if row.charge_type == "Actual": amount = flt(row.tax_amount)
			elif row.charge_type == "On Net Total": amount = taxable_net * flt(row.rate) / 100
			elif row.charge_type == "On Previous Row Amount": amount = previous_amount * flt(row.rate) / 100
			elif row.charge_type == "On Previous Row Total": amount = previous_total * flt(row.rate) / 100
			else: frappe.throw(_("Row {0}: invalid Tax Charge Type.").format(row.idx))
			row.tax_amount, running_total = amount, running_total + amount
			row.total, previous_amount, previous_total = running_total, amount, running_total
		return running_total - taxable_net

	def _calculate_profitability(self):
		revenue, cost = flt(self.estimated_selling_value_excluding_tax), flt(self.estimated_direct_cost)
		if self.cost_breakdown:
			cost = sum(flt(row.amount) for row in self.cost_breakdown)
			self.estimated_direct_cost = cost
		self.estimated_profit = revenue - cost
		self.estimated_margin_percent = self.estimated_profit / revenue * 100 if revenue else 0

	def _validate_downstream_lock(self):
		if self.is_new() or not frappe.db.exists("Logix Job", {"estimation": self.name}): return
		before = self.get_doc_before_save()
		if before and any(self.get(fieldname) != before.get(fieldname) for fieldname in COMMERCIAL_FIELDS):
			frappe.throw(_("Commercial fields are locked because a downstream Job exists. Use Cancel and Amend."))

	@frappe.whitelist()
	def apply_tax_template(self):
		self.check_permission("write")
		self.set("taxes", [])
		if self.taxes_and_charges_template:
			for source in frappe.get_doc("Sales Taxes and Charges Template", self.taxes_and_charges_template).taxes:
				self.append("taxes", {"charge_type":source.charge_type,"account_head":source.account_head,"description":source.description,"rate":source.rate,"tax_amount":source.tax_amount,"included_in_print_rate":source.included_in_print_rate})
		self._calculate_totals()
		return [row.as_dict() for row in self.taxes]

	@frappe.whitelist()
	def recalculate_commercials(self):
		self.validate()
		return {
			"items": [row.as_dict() for row in self.items], "taxes": [row.as_dict() for row in self.taxes],
			"net_total": self.net_total, "additional_discount_percentage": self.additional_discount_percentage,
			"additional_discount_amount": self.additional_discount_amount,
			"total_taxes_and_charges": self.total_taxes_and_charges, "grand_total": self.grand_total,
			"estimated_selling_value_excluding_tax": self.estimated_selling_value_excluding_tax,
			"estimated_profit": self.estimated_profit, "estimated_margin_percent": self.estimated_margin_percent,
		}

	def mark_accepted(self):
		self.status = "Accepted"
		self.save(ignore_permissions=True)


@frappe.whitelist()
def get_connected_jobs(estimation):
	doc = frappe.get_doc("Logix Estimation", estimation); doc.check_permission("read")
	return frappe.get_all("Logix Job", filters={"estimation": estimation}, fields=["name", "status", "customer", "branch", "creation"], order_by="creation desc")


def validate_estimation(doc, method=None):
	doc.run_method("validate")
