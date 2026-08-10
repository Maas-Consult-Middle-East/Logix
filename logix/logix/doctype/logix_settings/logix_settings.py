from __future__ import annotations
from frappe.model.document import Document


class LogixSettings(Document):
    """Server-side controller for the singleton Logix Settings doctype.

    Keeps thin authoritative server-side logic here. Additional validation
    and access helpers should be added as features evolve.
    """

    pass


def get_logix_settings() -> LogixSettings:
    """Utility to fetch the singleton settings doc.

    Example:
        settings = get_logix_settings()
        if settings.disallow_job_without_estimation:
            ...
    """
    import frappe

    return frappe.get_single("Logix Settings")
