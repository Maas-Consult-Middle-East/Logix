import frappe


CROSS_BRANCH_ROLES = {"System Manager", "Logix Manager"}


def allowed_branches(user=None):
	user = user or frappe.session.user
	if CROSS_BRANCH_ROLES.intersection(frappe.get_roles(user)):
		return None
	branches = set(frappe.get_all("User Permission", filters={"user": user, "allow": "Branch"}, pluck="for_value"))
	default_branch = frappe.db.get_value("User", user, "logix_branch")
	if default_branch:
		branches.add(default_branch)
	return sorted(branches)


def get_branch_query_conditions(doctype, user=None):
	branches = allowed_branches(user)
	if branches is None:
		return ""
	if not branches:
		return "1=0"
	escaped = ", ".join(frappe.db.escape(branch) for branch in branches)
	return f"`tab{doctype}`.`branch` in ({escaped})"


def estimation_query(user=None):
	return get_branch_query_conditions("Logix Estimation", user)


def job_query(user=None):
	return get_branch_query_conditions("Logix Job", user)


def shipment_order_query(user=None):
	return get_branch_query_conditions("Logix Shipment Order", user)


def shipment_query(user=None):
	return get_branch_query_conditions("Logix Shipment", user)


def trip_query(user=None):
	return get_branch_query_conditions("Logix Trip", user)


def has_branch_permission(doc, user=None, permission_type=None):
	branches = allowed_branches(user)
	return branches is None or bool(doc.branch and doc.branch in branches)
