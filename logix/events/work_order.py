import frappe


@frappe.whitelist()
def create_material_transfer(job_order, items):

    if isinstance(items, str):
        items = frappe.parse_json(items)

    if not items:
        frappe.throw("Please add at least one item.")

    stock_entry = frappe.new_doc("Stock Entry")

    stock_entry.stock_entry_type = "Material Transfer"

    stock_entry.from_warehouse = "Stores - L"
    stock_entry.to_warehouse = "Work In Progress - L"

    for row in items:

        if not row.get("item_code"):
            frappe.throw("Item Code is required.")

        if not row.get("qty"):
            frappe.throw(
                f"Quantity is required for Item {row.get('item_code')}"
            )

        stock_entry.append(
            "items",
            {
                "item_code": row.get("item_code"),
                "qty": row.get("qty"),
                "s_warehouse": "stores - L",
                "t_warehouse": "Work In Progress - L",
                "allow_zero_valuation_rate": 1
            }
        )

    stock_entry.insert(ignore_permissions=True)

    return stock_entry.name