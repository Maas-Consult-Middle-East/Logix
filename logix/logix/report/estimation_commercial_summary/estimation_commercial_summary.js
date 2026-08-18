frappe.query_reports["Estimation Commercial Summary"] = {
	filters: [
		{fieldname:"customer", label:__("Customer"), fieldtype:"Link", options:"Customer"},
		{fieldname:"contract_rate", label:__("Contract Rate"), fieldtype:"Link", options:"Logix Contract Rate"},
		{fieldname:"from_date", label:__("From Date"), fieldtype:"Date"},
		{fieldname:"to_date", label:__("To Date"), fieldtype:"Date"},
	],
};
