frappe.query_reports["Fuel Analytics"] = {
	filters: [
		{ fieldname: "from_date", label: __("From Date"), fieldtype: "Date", default: frappe.datetime.month_start() },
		{ fieldname: "to_date", label: __("To Date"), fieldtype: "Date", default: frappe.datetime.month_end() },
		{ fieldname: "branch", label: __("Branch"), fieldtype: "Link", options: "Branch" },
		{ fieldname: "vehicle", label: __("Vehicle"), fieldtype: "Link", options: "Vehicle" },
		{ fieldname: "driver", label: __("Driver"), fieldtype: "Link", options: "Driver" },
		{ fieldname: "abnormal_only", label: __("Abnormal Only"), fieldtype: "Check", default: 0 },
	],
};
