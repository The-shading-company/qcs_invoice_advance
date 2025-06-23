import frappe

def sync_logo_costs(doc, _):
    """Update logo_unit_selling in each child row based on logo_unit_cost and multiplier."""

    multiplier = frappe.db.get_single_value("TSC Logo Setup", "selling_multiplier") or 1

    for row in doc.logos:
        cost = row.logo_unit_cost or 0
        selling = cost * multiplier

        if row.logo_unit_selling != selling:
            row.logo_unit_selling = selling