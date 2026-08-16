// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Fuel Transaction", {
	setup(frm) {
		frm.set_query("trip", () => ({
			filters: { docstatus: ["<", 2], status: ["!=", "Cancelled"] },
		}));
	},

	trip(frm) {
		if (!frm.doc.trip) return;
		frappe.db.get_value("Logix Trip", frm.doc.trip, ["vehicle", "driver", "branch"]).then(({ message }) => {
			frm.set_value({ vehicle: message.vehicle, driver: message.driver, branch: message.branch });
		});
	},

	refresh(frm) {
		if (frm.doc.docstatus !== 1 || frm.doc.purchase_invoice || !frappe.model.can_create("Purchase Invoice")) {
			return;
		}
		frm.add_custom_button(
			__("Purchase Invoice"),
			() => frappe.model.open_mapped_doc({ method: "logix.api.make_purchase_invoice_from_fuel", frm }),
			__("Create")
		);
		frm.page.set_inner_btn_group_as_primary(__("Create"));
	},
});
