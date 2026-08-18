frappe.ui.form.on("Logix Estimation", {
	setup(frm) {
		frm.set_query("contract_rate", () => ({
			filters: {
				customer: frm.doc.customer || "",
				currency: frm.doc.currency || "",
				disabled: 0,
				requires_review: 0,
				applicable_from: ["<=", frm.doc.estimation_date || frappe.datetime.get_today()],
				applicable_to: [">=", frm.doc.estimation_date || frappe.datetime.get_today()],
			},
		}));
	},
	refresh(frm) {
		frm.toggle_display("costing_tab", Boolean(frm.doc.__onload && frm.doc.__onload.can_view_costing));
		render_connections(frm);
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__("Recalculate Commercials"), () => recalculate(frm));
		}
		if (frm.doc.docstatus === 1 && frm.doc.status === "Accepted") {
			frm.add_custom_button(__("Job"), () => {
				frappe.model.open_mapped_doc({ method: "logix.api.make_job", frm });
			}, __("Create"));
		}
	},
	customer(frm) {
		if (!frm.doc.contract_rate) return;
		frappe.db.get_value("Logix Contract Rate", frm.doc.contract_rate, "customer").then(({ message }) => {
			if (message && message.customer !== frm.doc.customer) {
				frm.set_value("contract_rate", null);
				mark_contract_rows_for_repricing(frm);
				frappe.show_alert({ message: __("Contract Rate was cleared because the Customer changed. Contract-priced rows require recalculation."), indicator: "orange" });
			}
		});
	},
	estimation_date(frm) { warn_invalid_contract(frm); },
	currency(frm) { warn_invalid_contract(frm); },
	contract_rate(frm) {
		if (!frm.doc.contract_rate) return;
		frappe.db.get_value("Logix Contract Rate", frm.doc.contract_rate, ["currency", "customer"]).then(({ message }) => {
			if (!message) return;
			if (!frm.doc.currency) frm.set_value("currency", message.currency);
			if (frm.doc.currency && frm.doc.currency !== message.currency) {
				frm.set_value("contract_rate", null);
				frappe.throw(__("The selected Contract Rate uses currency {0}. Change the Estimation currency first.", [message.currency]));
			}
		});
		if ((frm.doc.items || []).some(row => row.pricing_source === "Contract Rate")) {
			mark_contract_rows_for_repricing(frm);
			frappe.msgprint(__("Contract-derived rows are marked for recalculation. Manual and override rows were retained."));
		}
	},
	taxes_and_charges_template(frm) {
		frm.call("apply_tax_template").then(response => {
			frm.doc.taxes = response.message || [];
			frm.refresh_field("taxes");
			recalculate(frm);
		});
	},
});

frappe.ui.form.on("Logix Estimation Item", {
	form_render(frm, cdt, cdn) { configure_item_row(frm, locals[cdt][cdn]); },
	bill_by(frm, cdt, cdn) { configure_item_row(frm, locals[cdt][cdn]); },
	rate(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (row.pricing_source === "Contract Rate" && flt(row.suggested_rate) !== flt(row.rate)) {
			frappe.model.set_value(cdt, cdn, "manual_rate_override", 1);
			frappe.show_alert({message: __("Provide an Override Reason before saving."), indicator: "orange"});
		}
	},
});

function configure_item_row(frm, row) {
	const grid_row = frm.fields_dict.items.grid.grid_rows_by_docname[row.name];
	if (!grid_row || !grid_row.grid_form) return;
	const visible = {
		Route: ["from_city", "to_city", "vehicle_type", "load_type", "rate", "number_of_stops", "description"],
		Weight: ["weight", "weight_uom", "vehicle_type", "load_type", "rate", "description"],
		CBM: ["cbm", "vehicle_type", "load_type", "rate", "description"],
		Manual: ["description", "qty", "rate", "amount"],
	}[row.bill_by] || [];
	["from_city", "to_city", "vehicle_type", "load_type", "weight", "weight_uom", "cbm", "qty", "rate", "number_of_stops", "description"].forEach(fieldname => {
		grid_row.grid_form.toggle_display(fieldname, visible.includes(fieldname));
	});
}

function mark_contract_rows_for_repricing(frm) {
	(frm.doc.items || []).forEach(row => {
		if (row.pricing_source === "Contract Rate") {
			frappe.model.set_value(row.doctype, row.name, "needs_repricing", 1);
			frappe.model.set_value(row.doctype, row.name, "contract_service", null);
		}
	});
}

function warn_invalid_contract(frm) {
	if (!frm.doc.contract_rate) return;
	frappe.db.get_value("Logix Contract Rate", frm.doc.contract_rate, ["currency", "applicable_from", "applicable_to"]).then(({ message }) => {
		if (!message) return;
		const invalid = message.currency !== frm.doc.currency || frm.doc.estimation_date < message.applicable_from || frm.doc.estimation_date > message.applicable_to;
		if (invalid) frappe.show_alert({message: __("The selected Contract Rate is no longer valid for this date/currency. Correct it before submission."), indicator: "red"});
	});
}

function recalculate(frm) {
	return frm.call("recalculate_commercials").then(response => {
		const values = response.message || {};
		Object.assign(frm.doc, values);
		frm.refresh_fields(["items", "taxes", "net_total", "additional_discount_percentage", "additional_discount_amount", "total_taxes_and_charges", "grand_total", "estimated_selling_value_excluding_tax", "estimated_profit", "estimated_margin_percent"]);
	});
}

function render_connections(frm) {
	const wrapper = frm.get_field("connections_html").$wrapper;
	if (frm.is_new()) {
		wrapper.html(`<div class="text-muted">${__("No Job created from this Estimation yet.")}</div>`);
		return;
	}
	frappe.call("logix.logix.doctype.logix_estimation.logix_estimation.get_connected_jobs", {estimation: frm.doc.name}).then(({message}) => {
		const jobs = message || [];
		if (!jobs.length) {
			wrapper.html(`<div class="text-muted">${__("No Job created from this Estimation yet.")}</div>`);
			return;
		}
		const rows = jobs.map(job => `<tr><td><a href="/app/logix-job/${encodeURIComponent(job.name)}">${frappe.utils.escape_html(job.name)}</a></td><td>${frappe.utils.escape_html(job.status || "")}</td><td>${frappe.utils.escape_html(job.customer || "")}</td><td>${frappe.utils.escape_html(job.branch || "")}</td><td>${frappe.datetime.str_to_user(job.creation)}</td></tr>`).join("");
		wrapper.html(`<div class="table-responsive"><table class="table table-bordered"><thead><tr><th>${__("Job Number")}</th><th>${__("Job Status")}</th><th>${__("Customer")}</th><th>${__("Branch")}</th><th>${__("Creation Date")}</th></tr></thead><tbody>${rows}</tbody></table></div>`);
	});
}
