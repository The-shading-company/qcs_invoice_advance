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