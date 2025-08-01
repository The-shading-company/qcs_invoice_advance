import frappe

def execute():
    if not frappe.db.has_column("Stock Entry", "is_subcontracted"):
        frappe.db.add_column("Stock Entry", "is_subcontracted", "int(1) default 0")