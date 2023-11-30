import frappe

def create_bom(self, event):
    if (self.variant_of == "CAN"):
                
        fab_abb = []
        awn_abb = []
        size = []
        flag = 0
        
        tab = self.attributes
        for i in range(0, len(tab)):
            
            if (tab[i].get("attribute") == "Fabric Color"):
                value = tab[i].get("attribute_value")
                i_att = frappe.get_doc("Item Attribute", tab[i].get("attribute"))
                att_tab = i_att.item_attribute_values
                for j in range(0, len(att_tab)):
                    if (att_tab[j].get("attribute_value") == value):
                        fab_abb.append(att_tab[j].get("abbr"))
                        
            if (tab[i].get("attribute") == "Canopy Type"):
                value = tab[i].get("attribute_value")
                i_att = frappe.get_doc("Item Attribute", tab[i].get("attribute"))
                att_tab = i_att.item_attribute_values
                for j in range(0, len(att_tab)):
                    if (att_tab[j].get("attribute_value") == value):
                        awn_abb.append(att_tab[j].get("abbr"))
                        
            if (tab[i].get("attribute") == "Size"):
                value = tab[i].get("attribute_value")
                i_att = frappe.get_doc("Item Attribute", tab[i].get("attribute"))
                att_tab = i_att.item_attribute_values
                for j in range(0, len(att_tab)):
                    if (att_tab[j].get("attribute_value") == value):
                        size.append(att_tab[j].get("abbr"))

        stich = frappe.get_all("TSC Stitching Cost")
        for i in stich:
            s_doc = frappe.get_doc("TSC Stitching Cost", i)
            s_tab = s_doc.cost_table_tab
            for j in range(0, len(s_tab)):

                                
                if (s_tab[j].get("canopy_type") == awn_abb[0] and s_tab[j].get("canopy_size") == size[0]):

                    if (frappe.get_all("BOM", filters={"item": self.name})):
                        bom = frappe.get_all("BOM", filters={"item": self.name})
                        for k in bom:
                            bom_doc = frappe.get_doc("BOM", k)
                            if(bom_doc.docstatus == 0):
                                bom_doc.items[0].qty = s_tab[j].get("canopy_qty")
                                bom_doc.fg_based_operating_cost = 1
                                bom_doc.operating_cost_per_bom_quantity = s_tab[j].get("no_flap_stitching_cost")
                                bom_doc.save(ignore_permissions=True)
                                bom_doc.submit()
                                flag = 1
                                frappe.msgprint("BOM Updated Successfully")
                                
                    else:
                        self.save(ignore_permissions=True)
                        item = []
                        item.append({
                            "item_code": fab_abb[0],
                            "qty": s_tab[j].get("canopy_qty"),
                        })
                                    
                        doc = frappe.new_doc("BOM")
                        doc.update({
                            "item": self.name,
                            "items": item,
                            "fg_based_operating_cost": 1,
                            "operating_cost_per_bom_quantity": s_tab[j].get("no_flap_stitching_cost")
                        })
                        doc.insert(ignore_permissions=True)
                        doc.submit()
                        flag = 1
                        frappe.msgprint("BOM Created Successfully")
            if flag == 0:
                frappe.msgprint("TSC Costing Table missing values, BOM wasnt created")
 
 
 
def update_bom(self, event):
    
     if (self.variant_of == "CAN"):
                
        fab_abb = []
        awn_abb = []
        size = []
        
        tab = self.attributes
        for i in range(0, len(tab)):
            
            if (tab[i].get("attribute") == "Fabric Color"):
                value = tab[i].get("attribute_value")
                i_att = frappe.get_doc("Item Attribute", tab[i].get("attribute"))
                att_tab = i_att.item_attribute_values
                for j in range(0, len(att_tab)):
                    if (att_tab[j].get("attribute_value") == value):
                        fab_abb.append(att_tab[j].get("abbr"))
                        
            if (tab[i].get("attribute") == "Canopy Type"):
                value = tab[i].get("attribute_value")
                i_att = frappe.get_doc("Item Attribute", tab[i].get("attribute"))
                att_tab = i_att.item_attribute_values
                for j in range(0, len(att_tab)):
                    if (att_tab[j].get("attribute_value") == value):
                        awn_abb.append(att_tab[j].get("abbr"))
                        
            if (tab[i].get("attribute") == "Size"):
                size.append(tab[i].get("abbr"))
      
        stich = frappe.get_all("TSC Stitching Cost")
        for i in stich:
            s_doc = frappe.get_doc("TSC Stitching Cost", i)
            s_tab = s_doc.cost_table_tab
            for j in range(0, len(s_tab)):
                if (s_tab[j].get("canopy_type") == awn_abb[0] and s_tab[j].get("canopy_size") == size[0]):
                    if (frappe.get_all("BOM", filters={"item": self.name, "docstatus":0})):
                        bom = frappe.get_all("BOM", filters={"item": self.name, "docstatus":0})
                        for k in bom:
                            bom_doc = frappe.get_doc("BOM", k)
                            bom_doc.items[0].qty = s_tab[j].get("canopy_qty")
                            bom_doc.fg_based_operating_cost = 1
                            bom_doc.operating_cost_per_bom_quantity = s_tab[j].get("no_flap_stitching_cost")
                            bom_doc.save(ignore_permissions=True)
                            frappe.msgprint("BOM Updated Successfully")
                            
                            
def delete_bom(self, event):
    
    if (frappe.get_all("BOM", filters={"item": self.name})):
        bom = frappe.get_all("BOM", filters={"item": self.name})
        for k in bom:
            bom_doc = frappe.get_doc("BOM", k)
            if (bom_doc.docstatus == 0 or bom_doc.docstatus == 2):
                frappe.delete_doc("BOM", bom_doc.name, ignore_permissions=True)
            if (bom_doc.docstatus == 1):
                bom_doc.cancel()
                frappe.delete_doc("BOM", bom_doc.name, ignore_permissions=True)


def add_sale_price(self, event):

    itemprice = frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Retail"})

    if frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Retail"}):
        for i in itemprice:
            ip_doc = frappe.get_doc("Item Price", i)
            ip_doc.price_list_rate = self.total_cost * 2.1
            ip_doc.save(ignore_permissions=True)
    else:
        frappe.errprint("retail-else")
        ip_doc = frappe.new_doc("Item Price")
        ip_doc.item_code = self.item
        ip_doc.price_list = "Retail"
        ip_doc.price_list_rate = self.total_cost * 2.1
        ip_doc.save(ignore_permissions=True)

    itemprice = frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Contract"})
    
    if frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Contract"}):
        for i in itemprice:
            ip_doc = frappe.get_doc("Item Price", i)
            ip_doc.price_list_rate = self.total_cost * 1.9
            ip_doc.save(ignore_permissions=True)
    else:
        ip_doc = frappe.new_doc("Item Price")
        ip_doc.item_code = self.item
        ip_doc.price_list = "Contract"
        ip_doc.price_list_rate = self.total_cost * 1.9
        ip_doc.save(ignore_permissions=True)

    itemprice = frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Dealer"})
    if frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Dealer"}):
        for i in itemprice:
            ip_doc = frappe.get_doc("Item Price", i)
            ip_doc.price_list_rate = self.total_cost * 1.75
            ip_doc.save(ignore_permissions=True)
    else:
        ip_doc = frappe.new_doc("Item Price")
        ip_doc.item_code = self.item
        ip_doc.price_list = "Dealer"
        ip_doc.price_list_rate = self.total_cost * 1.75
        ip_doc.save(ignore_permissions=True)


def tsc_custom_accounts(self, event):
    if self.doctype == "Sales Invoice":
        for item in self.items:
            if frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group }):
                cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Expense" })
                item.expense_account = cogs[0].name
            if frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group }):
                rev = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Income" })
                item.income_account = rev[0].name

    if self.doctype == "Delivery Note":
        for item in self.items:
            if frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_group"), "custom_item_group":item.item_group }):
                cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_group"), "custom_item_group":item.item_group, "root_type":"Expense" })
                item.expense_account = cogs[0].name

                
