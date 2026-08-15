// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Job", {
	setup(frm) {
		frm.set_query("estimation", () => ({
			filters: {
				docstatus: 1,
				downstream_job: ["is", "not set"],
			},
		}));
	},

	refresh(frm) {
		if (!frm.is_new() && frm.doc.docstatus !== 2) {
			frm.add_custom_button(
				__("Shipment Order"),
				() => {
					frappe.model.open_mapped_doc({
						method: "logix.api.make_shipment_order",
						frm,
					});
				},
				__("Create")
			);
			frm.add_custom_button(
				__("Shipment"),
				() => {
					frappe.model.open_mapped_doc({
						method: "logix.api.make_shipment",
						frm,
					});
				},
				__("Create")
			);
			frm.page.set_inner_btn_group_as_primary(__("Create"));
		}

		if (frm.doc.docstatus !== 0) {
			return;
		}

		frm.add_custom_button(
			__("Estimation"),
			() => {
				erpnext.utils.map_current_doc({
					method: "logix.api.make_job",
					source_doctype: "Logix Estimation",
					target: frm,
					setters: {
						customer: frm.doc.customer || undefined,
					},
					get_query_filters: {
						docstatus: 1,
						downstream_job: ["is", "not set"],
					},
				});
			},
			__("Fetch From")
		);
	},
});
