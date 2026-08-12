import re

import frappe
from frappe.model.naming import NamingSeries

from logix.patches.v1_0_4_add_logix_naming_series import NAMING_SERIES


def execute():
	"""Continue native Naming Series counters from existing format-based names."""
	for doctype, naming_series in NAMING_SERIES.items():
		prefix = NamingSeries(naming_series).get_prefix()
		pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
		existing_names = frappe.get_all(
			doctype,
			filters={"name": ["like", f"{prefix}%"]},
			pluck="name",
			limit_page_length=0,
		)
		current = max(
			(int(match.group(1)) for name in existing_names if (match := pattern.fullmatch(name))),
			default=0,
		)
		if current:
			frappe.db.sql(
				"""
				insert into `tabSeries` (`name`, `current`)
				values (%s, %s)
				on duplicate key update `current` = greatest(`current`, values(`current`))
				""",
				(prefix, current),
			)
