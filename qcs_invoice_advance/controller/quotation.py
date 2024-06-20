import frappe

def update_service_call(self, event)
    doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
    doc.quote = self.name
    doc.save(ignore_permissions=True)