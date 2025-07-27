import frappe

def cron_update_product_bundle():
    """
    Cron: updates all Product Bundles with total component costs.
    Does NOT update Item Price of the bundle.
    """
    bundles = frappe.get_all("Product Bundle", filters={"disabled": 0}, fields=["name"])

    for b in bundles:
        doc = frappe.get_doc("Product Bundle", b.name)
        total_cost = 0

        for row in doc.items:
            item = frappe.get_doc("Item", row.item_code)

            row.custom_average_rate = float(item.custom_average_cost or 0)
            row.custom_item_validation_rate = float(item.valuation_rate or 0)
            row.custom_in_stock = get_item_stock(item.name)

            # decide which cost to use
            if row.custom_average_rate > 0:
                row.custom_item_cost = row.custom_average_rate
            else:
                row.custom_item_cost = row.custom_item_validation_rate

            row.custom_item_total_cost = (row.qty or 0) * row.custom_item_cost
            total_cost += row.custom_item_total_cost

        doc.custom_item_total_cost = total_cost
        doc.save(ignore_permissions=True)

        frappe.logger().info(f"[Bundle] Updated: {doc.name} — total cost: {total_cost}")


def get_item_stock(item_code):
    """
    Returns total stock quantity of an item.
    """
    qty = frappe.db.sql("""
        SELECT COALESCE(SUM(actual_qty), 0)
        FROM `tabBin`
        WHERE item_code = %s
    """, (item_code,))[0][0]

    return qty


@frappe.whitelist()
def get_valuation(item_code):
    """
    Get latest valuation rate of an item.
    """
    rate = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s
        ORDER BY posting_date DESC, posting_time DESC
        LIMIT 1
    """, (item_code,))

    rate = rate[0][0] if rate else None

    if not rate:
        rate = frappe.db.get_value("Item", item_code, "valuation_rate")

    return rate or 0


def cal_cost(self, event):
    """
    Hook: calculate and set total cost of components in a document.
    """
    if not self.items:
        return

    total_cost = 0

    for row in self.items:
        row.custom_item_total_cost = float((row.qty or 0) * (row.custom_item_cost or 0))
        total_cost += row.custom_item_total_cost

    self.custom_item_total_cost = total_cost



# def cal_cost(self, event):
#     if self.items:
#         tab = self.items
#         avg_rate = []
#         for i in range(0, len(tab)):
#             item_cost = float((tab[i].get("qty") or 0) * (tab[i].get("custom_item_cost") or 0))
#             tab[i].custom_item_total_cost = float(item_cost)
#             avg_rate.append(float(item_cost))
#         self.custom_item_total_cost = sum(avg_rate)
        
        
# @frappe.whitelist()
# def get_valuation(item_code):
#     valuation_rate = frappe.db.sql("""
#         SELECT valuation_rate
#         FROM `tabStock Ledger Entry`
#         WHERE item_code = %s
#         ORDER BY posting_date DESC, posting_time DESC
#         LIMIT 1
#     """, item_code)
    
#     valuation_rate = valuation_rate[0][0] if valuation_rate else None

#     if not valuation_rate:
#         valuation_rate = frappe.db.get_value("Item", item_code, "valuation_rate")
    
#     if valuation_rate:
#         return valuation_rate
#     else:
#         return 0
    
# def cron_update_product_bundle():
#     doc = frappe.get_all("Product Bundle", filters={"disabled":0}, fields=["name"])
#     if doc:
#         for i in doc:
#             doc1 = frappe.get_doc("Product Bundle", i.get("name"))
#             tab = doc1.items
#             cost = []
#             for j in range(0, len(tab)):
#                 item_code = tab[j].get("item_code")
#                 item_doc = frappe.get_doc("Item", item_code)
#                 stock = bundle_item_stock(item_code)
#                 tab[j].custom_average_rate = item_doc.custom_average_cost or 0
#                 tab[j].custom_item_validation_rate = item_doc.valuation_rate or 0
#                 tab[j].custom_in_stock = stock
#                 if float(item_doc.custom_average_cost) > 0:
#                     tab[j].custom_item_cost = float(item_doc.custom_average_cost) or 0
#                     tab[j].custom_item_total_cost = (tab[j].get("qty") or 0) * (tab[j].get("custom_item_cost") or 0)
#                     cost.append(tab[j].get("custom_item_total_cost") or 0)
#                 else:
#                     tab[j].custom_item_cost = item_doc.valuation_rate or 0
#                     tab[j].custom_item_total_cost = (tab[j].get("qty") or 0) * (tab[j].get("custom_item_cost") or 0)
#                     cost.append(tab[j].get("custom_item_total_cost") or 0)
#             doc1.custom_item_total_cost = sum(cost)
#             doc1.save(ignore_permissions=True)
            
@frappe.whitelist()
def bundle_item_stock(item_code):
    up_bin_qty = []
    bin_doc = frappe.get_all("Bin", filters={"item_code": item_code}, fields=["name", "actual_qty"])
    if bin_doc:
        for j in bin_doc:
            up_bin_qty.append(j.get("actual_qty"))
    else:
        up_bin_qty.append(0)

    qty = sum(up_bin_qty)
    return qty
