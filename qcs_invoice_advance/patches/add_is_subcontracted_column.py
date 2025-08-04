import frappe

def execute():
    if not frappe.db.has_column("Stock Entry", "is_subcontracted"):
        frappe.db.sql("""
            ALTER TABLE `tabStock Entry`
            ADD COLUMN `is_subcontracted` INT(1) DEFAULT 0
        """)
