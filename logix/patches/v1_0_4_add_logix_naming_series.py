import frappe


NAMING_SERIES = {
	"Logix Estimation": "EST-.YYYY.-",
	"Logix Handover": "HND-",
	"Logix Job": "JOB-.YYYY.-",
	"Logix Shipment": "SHP-.YYYY.-",
	"Logix Shipment Leg": "LEG-",
	"Logix Shipment Order": "SO-.YYYY.-",
	"Logix Transport Rate Card": "TRC-",
	"Logix Trip Plan": "TPL-.YYYY.-",
	"Logix Trip": "TRIP-.YYYY.-",
}


def execute():
	"""Backfill the selector on records created before Naming Series was enabled."""
	for doctype, naming_series in NAMING_SERIES.items():
		frappe.db.set_value(
			doctype,
			{"naming_series": ["is", "not set"]},
			"naming_series",
			naming_series,
			update_modified=False,
		)
		frappe.db.set_value(
			doctype,
			{"naming_series": ""},
			"naming_series",
			naming_series,
			update_modified=False,
		)
