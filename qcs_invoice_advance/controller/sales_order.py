
import frappe
import json

@frappe.whitelist()
def create_partial_invoice(sales_order, percentage):
    percentage = json.loads(percentage)
    so = frappe.get_doc("Sales Order", sales_order)
    
    doc = frappe.new_doc("Sales Invoice")
    item = []
    tab = so.items
    for i in range(0, len(tab)):
        qty = tab[i].get("qty")
        per = percentage
        percentage_decimal = per / 100
        balance = percentage_decimal * qty
        rounded_qty = round(balance)
        item.append({
            "item_code": tab[i].get("item_code"),
            "qty": rounded_qty,
            "original_qty": tab[i].get("qty"),
            "rate": tab[i].get("rate"),
            "amount": tab[i].get("amount"),
            "sales_order": sales_order,
            "so_detail": tab[i].get("name"),
        })
    doc.update({
        "customer": so.customer,
        "company": so.company,
        "due_date": so.delivery_date,
        "items": item,
        "original_total": so.total,
        "taxes_and_charges": so.taxes_and_charges,
        "vat_emirate": so.vat_emirate
    })
    doc.save(ignore_permissions=True)
    frappe.msgprint("Partial Sales Invoice created successfully.")
    return doc.name