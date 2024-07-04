import frappe
from frappe import _


def check_transferred_qty(self, event):             
    if (self.items):
        if (self.work_order):
            if (self.items):
                tab = self.items
                work_order = frappe.get_doc("Work Order", self.work_order)
                work_tab = work_order.required_items
                for i in range(0, len(tab)):
                    for j in range(0, len(work_tab)):
                        if (tab[i].get("idx") == work_tab[j].get("idx")):
                            if (tab[i].get("qty") > work_tab[j].get("required_qty")):
                                pass
                                #frappe.throw(_("Transferred Qty is More than Required Qty. To Check {0} Line Item in Work Order").format(tab[i].get("item_code")))
                                
                            if (tab[i].get("qty") < work_tab[j].get("required_qty")):
                                pass
                                #frappe.throw(_("Transferred Qty is Less than Required Qty. To Check {0} Line Item in Work Order").format(tab[i].get("item_code")))
