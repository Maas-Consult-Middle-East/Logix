from __future__ import annotations
import frappe
from frappe import _
from frappe.utils import flt
from frappe.model.document import Document


class LogixEstimation(Document):
    def validate(self):
        # Compute simple estimated profit and margin when revenue and cost present
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
            protected = ("customer", "branch", "estimated_revenue", "estimated_direct_cost")
            if before and any(self.get(field) != before.get(field) for field in protected):
                frappe.throw(_("Commercial fields are locked because Job {0} exists.").format(self.downstream_job))

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
