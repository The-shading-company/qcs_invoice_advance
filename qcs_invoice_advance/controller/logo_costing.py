import frappe

def sync_parent_logo_cost(doc, _):
    """Update parent Logo Costing doc when a Logo Costing Form row is saved."""
    if not (doc.logo_costing_id and doc.name):
        return

    multiplier = frappe.db.get_single_value("TSC Logo Setup", "selling_multiplier") or 1
    parent = frappe.get_doc("TSC Logo Costing", doc.logo_costing_id)

    row = next((r for r in parent.logos if r.name == doc.name), None)
    if not row:
        return

    new_cost = doc.logo_unit_cost
    new_selling = new_cost * multiplier

    if row.logo_unit_cost == new_cost and row.logo_unit_selling == new_selling:
        return  # No change, no save needed

    row.logo_unit_cost = new_cost
    row.logo_unit_selling = new_selling
    parent.save(ignore_permissions=True)