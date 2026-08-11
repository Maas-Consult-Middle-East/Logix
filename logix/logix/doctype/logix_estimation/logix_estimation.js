// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Estimation", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.doc.downstream_job) {
			frm.add_custom_button(__("Apply Rate Card"), () => {
				frm.call("preview_rate_card").then((response) => {
					const values = response.message || {};
					frm.set_value("pricing_source", "Rate Card");
					frm.set_value("rate_card", values.rate_card);
					frm.set_value("estimated_revenue", values.estimated_revenue);
					frm.set_value("currency", values.currency);
				});
			});
		}
	},
});
