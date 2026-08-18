frappe.ui.form.on("Logix Contract Rate", {
	refresh(frm) {
		frm.set_df_property("requires_review", "description", __("Disabled legacy rate preserved for commercial review."));
	},
});
