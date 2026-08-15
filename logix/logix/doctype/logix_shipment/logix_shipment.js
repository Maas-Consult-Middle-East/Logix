// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Shipment", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.docstatus === 2 || frm.doc.remaining_quantity <= 0) {
			return;
		}

		frm.add_custom_button(
			__("Trip Plan"),
			() => {
				frappe.model.open_mapped_doc({
					method: "logix.api.make_trip_plan",
					frm,
				});
			},
			__("Create")
		);
		frm.add_custom_button(
			__("Trip"),
			() => {
				frappe.model.open_mapped_doc({
					method: "logix.api.make_trip_from_shipment",
					frm,
				});
			},
			__("Create")
		);
		frm.page.set_inner_btn_group_as_primary(__("Create"));
	},
});
