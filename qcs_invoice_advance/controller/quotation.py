import frappe

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

# def check_discounts(self, event):
# 	if self.net_total != self.total:
# 		if self.selling_price_list == "Retail":
# 			if self.net_total >= self.total * 0.10:
# 				frappe.throw(_("Total Discount more than 10%"))
# 		if self.selling_price_list == "Contract":
# 			if self.net_total >= self.total * 0.05:
# 				frappe.throw(_("Total Discount more than 10%"))

#this checks discounts against the price list and calculated what the price list should be and ensures more than the max is not given
def check_discounts(doc, event=None):
    # Allow override for specific roles
    roles = frappe.get_roles(frappe.session.user)
    if "System Manager" in roles or "Accounts Manager" in roles:
        # Mark override to be logged later
        doc._discount_override_by = frappe.session.user
        return

    if not doc.items:
        return

    expected_total = 0.0

    for item in doc.items:
        # Use the official price from the selected price list
        standard_price = frappe.db.get_value("Item Price", {
            "item_code": item.item_code,
            "price_list": doc.selling_price_list
        }, "price_list_rate")

        if standard_price is None:
            frappe.throw(f"No price found for {item.item_code} in price list '{doc.selling_price_list}'")

        expected_total += (standard_price * item.qty)

    actual_total = doc.base_net_total
    discount_ratio = (expected_total - actual_total) / expected_total

    # Apply price-list-based limits with float safety
    if doc.selling_price_list == "Retail" and round(discount_ratio, 4) > 0.10:
        frappe.throw(_("Total discount exceeds 10% for Retail price list."))

    if doc.selling_price_list == "Contract" and round(discount_ratio, 4) > 0.05:
        frappe.throw(_("Total discount exceeds 5% for Contract price list."))

    if doc.selling_price_list == "Dealer" and round(discount_ratio, 4) > 0.0:
        frappe.throw(_("No discount allowed for Dealer price list."))

    # Absolute failsafe
    if discount_ratio > 0.20:
        frappe.throw(_("Total discount exceeds 20%, which is not allowed under any price list."))

def log_discount_override(doc, event=None):
    if getattr(doc, "_discount_override_by", None):
        frappe.get_doc({
            "doctype": "Comment",
            "comment_type": "Comment",
            "reference_doctype": doc.doctype,
            "reference_name": doc.name,
            "content": f"Discount override allowed by {doc._discount_override_by}"
        }).insert(ignore_permissions=True)