import frappe
from frappe import _
from frappe.utils import flt

def update_service_call(self, event):
    if self.custom_tsc_service_call:
        doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
        doc.quote = self.name
        doc.save(ignore_permissions=True)


def update_related_links(doc, event=None):
    # Ensure the script runs only when a Quotation is being amended
    if doc.amended_from:
        old_quotation = frappe.get_doc("Quotation", doc.amended_from)

        # Preserve the Payment Link (custom_tsc_payment_link)
        if old_quotation.custom_tsc_payment_link:
            doc.custom_tsc_payment_link = old_quotation.custom_tsc_payment_link

        def column_exists(doctype, column_name):
            try:
                return column_name in [field.fieldname for field in frappe.get_meta(doctype).fields]
            except Exception as e:
                frappe.log_error(f"Error checking column {column_name} in {doctype}: {str(e)}")
                return False

        linked_doctypes = {
            "TSC Service Call": "quote",
            "TSC Site Visit": "quotation",
            "TSC Logo Costing": "quotation",
            "TSC Commission": "quotation",
            "TSC Local Costing": "quotation",
            "TSC Import Costing": "quotation",
            "TSC Drawings": "quotation"
        }

        for doctype, quotation_field in linked_doctypes.items():
            if not column_exists(doctype, quotation_field):
                frappe.log_error(f"Field '{quotation_field}' does not exist in {doctype}. Skipping.")
                continue

            linked_docs = frappe.get_all(
                doctype,
                filters={quotation_field: doc.amended_from},
                fields=["name"]
            )

            if not linked_docs:
                frappe.log_error(f"No records found in {doctype} linked to {doc.amended_from}")
                continue

            for linked_doc in linked_docs:
                # Remove the old reference
                frappe.db.set_value(doctype, linked_doc.name, quotation_field, None)

                # Add the new reference
                frappe.db.set_value(doctype, linked_doc.name, quotation_field, doc.name)

                frappe.log_error(f"Updated {doctype}: {linked_doc.name} -> Old Quotation Removed, New Quotation: {doc.name}")


def check_discounts(doc, event=None):
    if not doc.items:
        return

    margin_percent = flt(getattr(doc, "custom_margin_percent", 0))
    total_cost = flt(getattr(doc, "custom_total_cost", 0))
    minimum_margin = 110.0

    if total_cost <= 0:
        return

    if margin_percent >= minimum_margin:
        return

    roles = frappe.get_roles(frappe.session.user)
    if any(role in roles for role in ("System Manager", "Accounts Manager", "TSC Discount Override")):
        doc._discount_override_by = frappe.session.user
        return

    frappe.throw(
        _("Margin percent must be at least {0}%. Current margin: {1:.2f}%").format(
            minimum_margin,
            margin_percent,
        )
    )

def log_discount_override(doc, event=None):
    override_user = getattr(doc, "_discount_override_by", None)
    if not override_user:
        return

    frappe.get_doc({
        "doctype": "Comment",
        "comment_type": "Comment",
        "reference_doctype": doc.doctype,
        "reference_name": doc.name,
        "content": f"Discount override allowed by {override_user}"
    }).insert(ignore_permissions=True)

    # reset flag so hooks in the same request don't duplicate the comment
    doc._discount_override_by = None

def set_company(doc, method=None):
    # 1. Decide target company / tax template
    has_pergola = any(item.item_code and "PER-" in item.item_code for item in doc.items)

    if has_pergola:
        target_company = "The Shading Oasis Pergola Installation LLC"
        target_taxes   = "UAE VAT 5% - TSOPIL"
    else:
        target_company = "The Shading Umbrella Trading Co LLC"
        target_taxes   = "UAE VAT 5% - TSUTCL"

    # 2. Switch company first
    if doc.company != target_company:
        doc.company = target_company

    default_cc = frappe.get_value("Company", target_company, "cost_center")

    # ---------- NEW: realign every cost-centre ----------
    if getattr(doc, "cost_center", None) and doc.cost_center != default_cc:
        doc.cost_center = default_cc

    for row in doc.items:
        if getattr(row, "cost_center", None) != default_cc:
            row.cost_center = default_cc
    # ----------------------------------------------------

    # 3. Reset taxes & pull fresh rows
    doc.taxes_and_charges = target_taxes
    doc.set("taxes", [])

    template = frappe.get_doc("Sales Taxes and Charges Template", target_taxes)
    for row in template.taxes:
        # ensure account belongs to the company
        if frappe.get_value("Account", row.account_head, "company") != target_company:
            frappe.throw(f"Account {row.account_head} does not belong to {target_company}")

        # pick a company-correct cost centre
        cc = row.cost_center or default_cc
        if frappe.get_value("Cost Center", cc, "company") != target_company:
            cc = default_cc

        doc.append("taxes", {
            "charge_type"            : row.charge_type,
            "account_head"           : row.account_head,
            "description"            : row.description,
            "rate"                   : row.rate,
            "cost_center"            : cc,
            "included_in_print_rate" : row.included_in_print_rate,
        })

    # 4. Re-calculate totals
    doc.calculate_taxes_and_totals()