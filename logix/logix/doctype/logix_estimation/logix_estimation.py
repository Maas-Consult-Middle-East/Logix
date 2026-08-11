from __future__ import annotations
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document

from logix.services.pricing import calculate_transport_price


class LogixEstimation(Document):
    def validate(self):
        self.validate_transport_inputs()
        self.calculate_selling_price()

        revenue = flt(self.estimated_revenue)
        cost = flt(self.estimated_direct_cost)

        profit = revenue - cost
        self.estimated_profit = profit
        self.estimated_margin_percent = (profit / revenue * 100.0) if revenue else 0.0

        # Basic status validation
        allowed = ["Draft", "Submitted", "Sent to Customer", "Accepted", "Rejected"]
        if self.status and self.status not in allowed:
            frappe.throw(_("Invalid commercial status: {0}").format(self.status))

        if not self.is_new() and self.downstream_job:
            before = self.get_doc_before_save()
            protected = (
                "customer", "branch", "from_city", "to_city", "vehicle_type", "load_type",
                "base_weight", "cbm", "extra_stops", "trip_pricing", "pricing_source",
                "estimated_revenue", "estimated_direct_cost",
            )
            if before and any(self.get(field) != before.get(field) for field in protected):
                frappe.throw(_("Commercial fields are locked because Job {0} exists.").format(self.downstream_job))

    def validate_transport_inputs(self):
        if self.from_city == self.to_city:
            frappe.throw(_("From City and To City must be different."))
        if flt(self.base_weight) < 0 or flt(self.cbm) < 0 or int(self.extra_stops or 0) < 0:
            frappe.throw(_("Weight, CBM, and Extra Stops cannot be negative."))

    def calculate_selling_price(self):
        settings = frappe.get_single("Logix Settings")
        if self.pricing_source == "Manual":
            self.rate_card = None
            self.currency = self.currency or frappe.db.get_single_value("Global Defaults", "default_currency")
            if settings.rate_card_pricing_enabled and not settings.manual_pricing_allowed:
                frappe.throw(_("Manual pricing is disabled in Logix Settings."))
            return

        if not settings.rate_card_pricing_enabled:
            self.rate_card = None
            return

        result = calculate_transport_price(
            customer=self.customer,
            from_city=self.from_city,
            to_city=self.to_city,
            vehicle_type=self.vehicle_type,
            load_type=self.load_type,
            weight=self.base_weight,
            cbm=self.cbm,
            extra_stops=self.extra_stops,
            trip_pricing=self.trip_pricing or "One Way",
        )
        self.rate_card = result.rate_card
        self.estimated_revenue = result.amount
        self.currency = result.currency

    @frappe.whitelist()
    def preview_rate_card(self):
        self.pricing_source = "Rate Card"
        self.calculate_selling_price()
        return {
            "rate_card": self.rate_card,
            "estimated_revenue": self.estimated_revenue,
            "currency": self.currency,
        }

    def mark_accepted(self):
        """Convenience method to mark estimation accepted from downstream actions.

        Downstream creators (e.g. Job creation service) should call this method
        to ensure consistent acceptance behavior.
        """
        self.status = "Accepted"
        self.save(ignore_permissions=True)


def get_estimation(estim_name: str):
    return frappe.get_doc("Logix Estimation", estim_name)


def validate_estimation(doc, method=None):
    """Doc-event handler wrapper so hooks can call validation logic reliably.

    This function mirrors the controller's validate behaviour and is referenced
    via `doc_events` in `hooks.py` to ensure it runs even if class controller
    import mapping is inconsistent in some developer environments.
    """
    try:
        revenue = float(doc.estimated_revenue or 0)
    except Exception:
        revenue = 0.0
    try:
        cost = float(doc.estimated_direct_cost or 0)
    except Exception:
        cost = 0.0

    profit = revenue - cost
    doc.estimated_profit = profit
    doc.estimated_margin_percent = (profit / revenue * 100.0) if revenue else 0.0
