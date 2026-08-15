// Copyright (c) 2026, MAAS Consult and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logix Estimation", {
	refresh(frm) {
		if (frm.doc.vehicle_type) {
			update_vehicle_capacity(frm);
		} else {
			render_vehicle_capacity(frm, {});
		}

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

		if (frm.doc.docstatus === 1 && !frm.doc.downstream_job) {
			frm.add_custom_button(
				__("Job"),
				() => {
					frappe.model.open_mapped_doc({
						method: "logix.api.make_job",
						frm,
					});
				},
				__("Create")
			);
		}
	},
	vehicle_type: update_vehicle_capacity,
	base_weight: update_vehicle_capacity,
	cbm: update_vehicle_capacity,
});

let capacity_request = 0;

function update_vehicle_capacity(frm) {
	if (!frm.doc.vehicle_type) {
		render_vehicle_capacity(frm, {});
		return;
	}

	const request = ++capacity_request;
	frm.call("preview_vehicle_capacity").then((response) => {
		if (request !== capacity_request) {
			return;
		}
		const utilization = response.message || {};
		frm.doc.weight_utilization_percent = utilization.weight_utilization_percent || 0;
		frm.doc.volume_utilization_percent = utilization.volume_utilization_percent || 0;
		frm.doc.loading_percentage = utilization.loading_percentage || 0;
		frm.doc.capacity_basis = utilization.capacity_basis || "Not Configured";
		frm.refresh_fields([
			"weight_utilization_percent",
			"volume_utilization_percent",
			"loading_percentage",
			"capacity_basis",
		]);
		render_vehicle_capacity(frm, utilization);
	});
}

function render_vehicle_capacity(frm, utilization) {
	const field = frm.get_field("capacity_visualization");
	if (!field) {
		return;
	}

	if (!frm.doc.vehicle_type) {
		field.$wrapper.html(
			'<div class="text-muted">' + __("Select a Vehicle Type to see its loading.") + "</div>"
		);
		return;
	}

	const raw_percentage = flt(utilization.loading_percentage);
	const percentage = Math.max(0, Math.min(100, raw_percentage));
	const red_width = (350 * percentage) / 100;
	const weight_percentage = flt(utilization.weight_utilization_percent);
	const volume_percentage = flt(utilization.volume_utilization_percent);
	const basis = utilization.capacity_basis || "Not Configured";
	const over_capacity = raw_percentage > 100;
	const status = over_capacity ? __("Over capacity") : __("Loaded");
	const vehicle = frappe.utils.escape_html(frm.doc.vehicle_type);
	const formatted_loading = format_number(raw_percentage, null, 1);

	field.$wrapper.html(
		[
			'<div style="max-width:680px;padding:12px 0">',
			'<div style="display:flex;justify-content:space-between;gap:12px;align-items:end;margin-bottom:8px">',
			'<div><div style="font-weight:600;font-size:14px">',
			vehicle,
			'</div><div class="text-muted">',
			__("Capacity limited by"),
			": ",
			__(basis),
			"</div></div>",
			'<div style="font-weight:700;font-size:20px;color:',
			over_capacity ? "var(--red-600)" : "var(--text-color)",
			'">',
			formatted_loading,
			"% ",
			status,
			"</div></div>",
			'<svg viewBox="0 0 430 165" role="img" aria-label="',
			formatted_loading,
			"% ",
			__("vehicle loaded"),
			'" style="display:block;width:100%;height:auto">',
			'<defs><clipPath id="logix-lorry-body"><rect x="30" y="38" width="255" height="82" rx="7"></rect><path d="M285 62 H340 L380 96 V120 H285 Z"></path></clipPath></defs>',
			'<g clip-path="url(#logix-lorry-body)"><rect x="30" y="30" width="350" height="100" fill="var(--green-500, #22a06b)"></rect>',
			'<rect x="30" y="30" width="',
			red_width,
			'" height="100" fill="var(--red-500, #e5484d)"></rect></g>',
			'<rect x="30" y="38" width="255" height="82" rx="7" fill="none" stroke="var(--gray-900, #1f272e)" stroke-width="5"></rect>',
			'<path d="M285 62 H340 L380 96 V120 H285 Z" fill="none" stroke="var(--gray-900, #1f272e)" stroke-width="5" stroke-linejoin="round"></path>',
			'<path d="M343 71 L368 96 H315 V71 Z" fill="var(--blue-100, #d7e9ff)" stroke="var(--gray-900, #1f272e)" stroke-width="4" stroke-linejoin="round"></path>',
			'<line x1="24" y1="122" x2="390" y2="122" stroke="var(--gray-900, #1f272e)" stroke-width="6" stroke-linecap="round"></line>',
			'<circle cx="105" cy="127" r="22" fill="var(--gray-900, #1f272e)"></circle><circle cx="105" cy="127" r="9" fill="var(--gray-300, #c9d0d8)"></circle>',
			'<circle cx="327" cy="127" r="22" fill="var(--gray-900, #1f272e)"></circle><circle cx="327" cy="127" r="9" fill="var(--gray-300, #c9d0d8)"></circle>',
			'<text x="157" y="88" text-anchor="middle" dominant-baseline="middle" fill="white" font-size="25" font-weight="700">',
			formatted_loading,
			"%</text></svg>",
			'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:6px">',
			'<span class="indicator-pill blue">',
			__("Weight"),
			": ",
			format_number(weight_percentage, null, 1),
			'%</span><span class="indicator-pill purple">',
			__("Volume"),
			": ",
			format_number(volume_percentage, null, 1),
			'%</span><span class="indicator-pill red">',
			__("Red"),
			": ",
			format_number(percentage, null, 1),
			"% ",
			__("used"),
			'</span><span class="indicator-pill green">',
			__("Green"),
			": ",
			format_number(100 - percentage, null, 1),
			"% ",
			__("available"),
			"</span></div></div>",
		].join("")
	);
}
