// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Trip", {
	refresh(frm) {
		if (frm.is_new() || frm.doc.docstatus === 2) {
			return;
		}

		if (frm.doc.vehicle && frm.doc.driver && frappe.model.can_create("Logix Fuel Transaction")) {
			frm.add_custom_button(
				__("Fuel Transaction"),
				() => frappe.new_doc("Logix Fuel Transaction", {
					trip: frm.doc.name,
					vehicle: frm.doc.vehicle,
					driver: frm.doc.driver,
					branch: frm.doc.branch,
				}),
				__("Create")
			);
		}

		const shipments = [
			...new Set(
				(frm.doc.allocations || [])
					.filter((row) => row.status !== "Removed" && row.shipment)
					.map((row) => row.shipment)
			),
		];
		if (!shipments.length) {
			return;
		}

		frm.add_custom_button(
			__("POD"),
			() => {
				if (shipments.length === 1) {
					open_pod(frm, shipments[0]);
					return;
				}

				const dialog = new frappe.ui.Dialog({
					title: __("Create POD"),
					fields: [
						{
							fieldname: "shipment",
							fieldtype: "Select",
							label: __("Shipment"),
							options: shipments,
							reqd: 1,
						},
					],
					primary_action_label: __("Create"),
					primary_action(values) {
						dialog.hide();
						open_pod(frm, values.shipment);
					},
				});
				dialog.show();
			},
			__("Create")
		);
		frm.page.set_inner_btn_group_as_primary(__("Create"));
	},
});

function open_pod(frm, shipment) {
	frappe.model.open_mapped_doc({
		method: "logix.api.make_pod",
		frm,
		args: { shipment },
	});
}
