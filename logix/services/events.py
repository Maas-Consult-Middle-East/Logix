import frappe
from frappe import _
from frappe.utils import now_datetime


SHIPMENT_TRANSITIONS = {
	"Draft": {"Ready for Planning"}, "Ready for Planning": {"Planned", "Assigned"},
	"Planned": {"Assigned"}, "Assigned": {"Pickup Pending", "Picked Up"},
	"Pickup Pending": {"Picked Up", "Failed Delivery"}, "Picked Up": {"In Transit"},
	"In Transit": {"At Handover", "Out for Delivery", "Failed Delivery", "Return to Origin"},
	"At Handover": {"In Transit"}, "Out for Delivery": {"Delivered", "Failed Delivery"},
	"Failed Delivery": {"Ready for Planning", "Return to Origin"},
}


def transition_shipment(shipment, new_status, event_type, trip=None, remarks=None, override_reason=None):
	doc = frappe.get_doc("Logix Shipment", shipment)
	doc.check_permission("write")
	previous = doc.status
	allowed = new_status in SHIPMENT_TRANSITIONS.get(previous, set())
	if not allowed:
		if "Logix Manager" not in frappe.get_roles() or not override_reason:
			frappe.throw(_("Transition from {0} to {1} is not allowed.").format(previous, new_status))
		remarks = _("Manager override: {0}").format(override_reason)
	doc.db_set("status", new_status)
	frappe.get_doc({
		"doctype": "Logix Shipment Event", "shipment": shipment, "trip": trip,
		"event_type": event_type, "event_time": now_datetime(), "event_user": frappe.session.user,
		"remarks": remarks, "previous_status": previous, "new_status": new_status,
	}).insert(ignore_permissions=True)
	return new_status
