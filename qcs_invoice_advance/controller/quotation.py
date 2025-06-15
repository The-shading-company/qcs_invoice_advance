import frappe

def update_service_call(self, event):
    if self.custom_tsc_service_call:
        doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
        doc.quote = self.name
        doc.save(ignore_permissions=True)


def update_related_links(self, event=None):
    if not self.amended_from:
        return

    old_quotation = frappe.get_doc("Quotation", self.amended_from)

    if old_quotation.custom_tsc_payment_link:
        self.custom_tsc_payment_link = old_quotation.custom_tsc_payment_link

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
        if quotation_field not in frappe.get_meta(doctype).fields_by_fieldname:
            continue

        linked_docs = frappe.get_all(
            doctype,
            filters={quotation_field: self.amended_from},
            fields=["name"]
        )

        for linked_doc in linked_docs:
            frappe.db.set_value(doctype, linked_doc.name, quotation_field, self.name)