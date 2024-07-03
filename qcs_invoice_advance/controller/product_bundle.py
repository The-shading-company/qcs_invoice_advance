import frappe


def cal_cost(self, event):
    if self.items:
        tab = self.items
        avg_rate = []
        for i in range(0, len(tab)):
            avg_rate.append(tab[i].get("custom_item_cost"))
        self.custom_item_total_cost = sum(avg_rate)
        
        
@frappe.whitelist()
def get_valuation(item_code):
    valuation_rate = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s
        ORDER BY posting_date DESC, posting_time DESC
        LIMIT 1
    """, item_code)
    
    valuation_rate = valuation_rate[0][0] if valuation_rate else None

    if not valuation_rate:
        valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate")
    
    if valuation_rate:
        return valuation_rate
    else:
        return 0
    
def cron_update_product_bundle():
    doc = frappe.get_all("Product Bundle", filters={"disabled":0}, fields=["name"])
    if doc:
        for i in doc:
            doc1 = frappe.get_doc("Product Bundle", i.get("name"))
            tab = doc1.items
            cost = []
            for j in range(0, len(tab)):
                item_code = tab[j].get("item_code")
                item_doc = frappe.get_doc("Item", item_code)
                tab[j].custom_average_rate = item_doc.custom_average_cost or 0
                tab[j].custom_item_validation_rate = item_doc.valuation_rate or 0
                if float(item_doc.custom_average_cost) > 0:
                    tab[j].custom_item_cost = float(item_doc.custom_average_cost) or 0
                    cost.append(float(item_doc.custom_average_cost) or 0)
                else:
                    tab[j].custom_item_cost = item_doc.valuation_rate or 0
                    cost.append(item_doc.valuation_rate or 0)
            doc1.custom_item_total_cost = sum(cost)
            doc1.save(ignore_permissions=True)