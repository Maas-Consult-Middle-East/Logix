import frappe


def mark_accepted(doc_or_name):
    if isinstance(doc_or_name, str):
        doc = frappe.get_doc("Logix Estimation", doc_or_name)
    else:
        doc = doc_or_name
    doc.status = "Accepted"
    doc.save()
    return doc.name
