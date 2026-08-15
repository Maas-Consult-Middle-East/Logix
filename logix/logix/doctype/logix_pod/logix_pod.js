// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix POD", {
	refresh(frm) {
		if (
			frm.doc.docstatus !== 1 ||
			frm.doc.status !== "Verified" ||
			!frappe.model.can_create("Sales Invoice")
		) {
			return;
		}

		frm.add_custom_button(
			__("Sales Invoice"),
			() => {
				frappe.model.open_mapped_doc({
					method: "logix.api.make_sales_invoice_from_pod",
					frm,
				});
			},
			__("Create")
		);
		frm.page.set_inner_btn_group_as_primary(__("Create"));
	},
});
