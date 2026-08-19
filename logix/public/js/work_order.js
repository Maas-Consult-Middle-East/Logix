frappe.ui.form.on("Work Order", {

    custom_production_status: function(frm) {

        if (frm.doc.custom_production_status === "In") {
            show_material_transfer_dialog(frm);
        }
    }

});


function show_material_transfer_dialog(frm) {

    frappe.db.get_list("Item Group", {
        filters: {
            parent_item_group: "Raw Material"
        },
        fields: ["name"],
        limit_page_length: 100
    }).then(item_groups => {

        // Child Item Groups of Raw Material
        let group_names = item_groups.map(row => row.name);

        // Also include Raw Material itself
        group_names.push("Raw Material");

        console.log("Allowed Item Groups:", group_names);

        let dialog = new frappe.ui.Dialog({
            title: "Stock Request",

            fields: [
                {
                    fieldname: "items",
                    fieldtype: "Table",
                    label: "Items",
                    cannot_add_rows: false,
                    in_place_edit: true,

                    fields: [
                        {
                            fieldname: "item_code",
                            fieldtype: "Link",
                            label: "Item",
                            options: "Item",
                            in_list_view: 1,
                            reqd: 1
                        },
                        {
                            fieldname: "qty",
                            fieldtype: "Float",
                            label: "Qty",
                            in_list_view: 1,
                            reqd: 1
                        }
                    ]
                }
            ],

            primary_action_label: "Create Material Transfer",

            primary_action(values) {

                if (!values.items || values.items.length === 0) {
                    frappe.msgprint("Please add at least one item.");
                    return;
                }

                frappe.call({
                    method: "logix.events.work_order.create_material_transfer",

                    args: {
                        job_order: frm.doc.name,
                        items: values.items
                    },

                    freeze: true,
                    freeze_message: "Creating Material Transfer...",

                    callback: function(r) {

                        if (r.message) {

                            dialog.hide();

                            frappe.set_route(
                                "Form",
                                "Stock Entry",
                                r.message
                            );
                        }
                    }
                });
            }
        });


        dialog.fields_dict.items.grid
            .get_field("item_code")
            .get_query = function() {

                return {
                    filters: {
                        item_group: ["in", group_names]
                    }
                };
            };


        dialog.show();
    });
}
