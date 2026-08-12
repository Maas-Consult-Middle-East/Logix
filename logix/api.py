import secrets

import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, now_datetime


def _validate_estimation_for_job(estimation):
	if estimation.docstatus != 1:
		frappe.throw(_("Only submitted Estimations can be used to create a Job."))
	if estimation.downstream_job:
		frappe.throw(_("Job {0} has already been created from this Estimation.").format(estimation.downstream_job))


@frappe.whitelist()
def make_job(source_name, target_doc=None):
	"""Map a submitted Estimation to a new or existing Job draft."""
	estimation = frappe.get_doc("Logix Estimation", source_name)
	estimation.check_permission("read")
	_validate_estimation_for_job(estimation)

	return get_mapped_doc(
		"Logix Estimation",
		source_name,
		{
			"Logix Estimation": {
				"doctype": "Logix Job",
				"field_map": {
					"name": "estimation",
					"estimated_revenue": "agreed_revenue",
					"estimated_direct_cost": "estimated_cost",
					"vehicle_type": "preferred_vehicle_type",
				},
				"field_no_map": ["naming_series", "status"],
				"validation": {"docstatus": ["=", 1]},
			},
		},
		target_doc,
	)


@frappe.whitelist()
def create_job_from_estimation(estimation):
	est = frappe.get_doc("Logix Estimation", estimation)
	est.check_permission("read")
	_validate_estimation_for_job(est)
	job = make_job(est.name)
	job.insert()
	frappe.db.set_value("Logix Estimation", est.name, {"status": "Accepted", "downstream_job": job.name})
	return job.name


@frappe.whitelist()
def regenerate_tracking_token(shipment):
	doc = frappe.get_doc("Logix Shipment", shipment)
	doc.check_permission("write")
	days = frappe.db.get_single_value("Logix Settings", "default_public_tracking_expiry_days") or 30
	doc.db_set({"tracking_token": secrets.token_urlsafe(32), "tracking_revoked": 0, "tracking_expires_on": add_days(now_datetime(), days)})
	return doc.tracking_token


@frappe.whitelist(allow_guest=True)
def public_tracking(token):
	if not isinstance(token, str) or len(token) < 32 or len(token) > 128:
		frappe.throw(_("Tracking link is invalid."), frappe.PermissionError)
	row = frappe.db.get_value(
		"Logix Shipment", {"tracking_token": token},
		["name", "status", "tracking_enabled", "tracking_revoked", "tracking_expires_on"], as_dict=True,
	)
	if not row or not row.tracking_enabled or row.tracking_revoked or not row.tracking_expires_on or row.tracking_expires_on < now_datetime():
		frappe.throw(_("Tracking link is invalid or expired."), frappe.PermissionError)
	milestones = frappe.get_all(
		"Logix Shipment Event", filters={"shipment": row.name},
		fields=["event_type", "event_time", "new_status"], order_by="event_time asc", limit_page_length=100,
	)
	return {"tracking_reference": token[-8:], "status": row.status, "milestones": milestones}
