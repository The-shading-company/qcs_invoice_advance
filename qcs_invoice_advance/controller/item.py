import frappe
from frappe.model.mapper import get_mapped_doc
import requests
import json
from frappe import _

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


def add_image(self, event):
	if (self.variant_of == "CAN"):
		for item in self.attributes:
			if item.attribute == "Fabric Color":
				att_list = frappe.get_all("Item Attribute Value", filters={"attribute_value":item.attribute_value})
				if len(att_list) > 0:
					att_raw = frappe.db.get_value("Item Attribute Value", {"attribute_value":item.attribute_value}, "custom_item_code")
					self.image = frappe.get_value("Item", att_raw, "image")
					



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
            cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Expense" })
            if len(cogs) > 0:
                item.expense_account = cogs[0].name
            rev = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Income" })
            if len(rev) > 0:
                item.income_account = rev[0].name

    if self.doctype == "Delivery Note":
        for item in self.items:
            cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Expense" })
            if len(cogs) > 0:
                item.expense_account = cogs[0].name


def add_margins(self, event):
	total_cost = 0
	total_margin = 0
	for item in self.items:
		bom = frappe.get_all("BOM", filters={"item": item.item_code, "is_active": 1, "is_default": 1})
		if len(bom) > 0:
			bom_index = frappe.get_doc("BOM", bom[0].name)
			item.custom_tsc_cost = bom_index.total_cost
			total_cost += item.custom_tsc_cost
		else:
			item.custom_tsc_cost = item.valuation_rate
			total_cost += item.custom_tsc_cost
		if item.custom_tsc_cost:
			item.custom_tsc_margin = item.rate - item.custom_tsc_cost
			total_margin += item.custom_tsc_margin
			item.custom_tsc_margin_per = (item.custom_tsc_margin * 100) / item.custom_tsc_cost
	self.custom_total_cost = total_cost
	self.custom_total_margin = self.net_total - total_cost
	self.custom_margin_percent = (self.custom_total_margin * 100) / self.custom_total_cost


def add_quote_link(self, event):
	if self.custom_tsc_site_visit:
		sv = frappe.get_doc("TSC Site Visit", self.custom_tsc_site_visit)
		sv.quotation = self.name
		sv.save(ignore_permissions=True)


def check_discounts(self, event):
	if self.net_total != self.total:
		if self.selling_price_list == "Retail":
			if self.net_total >= self.total * 0.10:
				frappe.throw(_("Total Discount more than 10%"))
		if self.selling_price_list == "Contract":
			if self.net_total >= self.total * 0.05:
				frappe.throw(_("Total Discount more than 10%"))
	
	

                

@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		#if not source.get("items", []):
		#	quotation.opportunity = source.name

	doclist = get_mapped_doc(
		"TSC Service Call",
		source_name,
		{
			"TSC Service Call": {
				"doctype": "Quotation",
				"field_map": {"customer": "party_name"},
			},
			"TSC Service Call Info": {
				"doctype": "Quotation Item",
				"field_map": {
					"uom": "stock_uom",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist



@frappe.whitelist()
def make_quotation_site_visit(source_name, target_doc=None):
	sv = frappe.get_doc("TSC Site Visit", source_name)
	
	cust = frappe.new_doc("Customer")
	if sv.customer_type == "Company":
		cust.customer_name = sv.organization_name
	if sv.customer_type == "Individual":
		cust.customer_name = sv.customer_name

	if not frappe.db.exists("Customer", cust.customer_name):
		cust.customer_group = sv.customer_group
		cust.customer_type = sv.customer_type
		cust.territory = sv.territory
		cust.save(ignore_permissions=True)
		if sv.customer_name:
			cont = frappe.new_doc("Contact")
			cont.first_name = sv.customer_name
			cont.append("phone_nos",{
				"phone": sv.mobile_no,
				"is_primary_mobile_no": 1
			})
			cont.append("links",{
				"link_doctype": "Customer",
				"link_name": cust.name
			})
			cont.save(ignore_permissions=True)
			address = frappe.new_doc("Address")
			address.address_title = sv.customer_name
			address.address_type = "Billing"
			address.address_line1 = sv.address
			address.country = "United Arab Emirates"
			address.is_primary_address = 1
			address.append("links",{
				"link_doctype": "Customer",
				"link_name": cust.name
			})
			address.save(ignore_permissions=True)
			
		
		
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		quotation.custom_tsc_site_visit = source.name
		#if not source.get("items", []):
		#	quotation.opportunity = source.name

	if sv.customer_type == "Company":
		doclist = get_mapped_doc(
			"TSC Site Visit",
			source_name,
			{
				
				"TSC Site Visit": {
					"doctype": "Quotation",
					"field_map": {"organization_name": "party_name"},
				},
			
			},
			target_doc,
			set_missing_values,
		)
	if sv.customer_type == "Individual":
		doclist = get_mapped_doc(
			"TSC Site Visit",
			source_name,
			{
				
				"TSC Site Visit": {
					"doctype": "Quotation",
					"field_map": {"customer_name": "party_name"},
				},
			
			},
			target_doc,
			set_missing_values,
		)

	return doclist


@frappe.whitelist()
def create_payment_link(dt, dn, amt, purpose):
	docu = frappe.get_doc(dt, dn)
	url = "https://simplify-rak-gbermhh3pa-uc.a.run.app/create"

	payload = json.dumps({
	  "key": "kl8EvdFF4EPPIo5JHJto74lz-EOt5rabkmnE",
	  "reference": dn,
	  "note": "test",
	  "dueDate": str(docu.transaction_date),
	  "memo": "Delivery To",
	  "name": docu.customer_name,
	  "email": docu.contact_email if docu.contact_email else "",
	  "description": purpose,
	  "amount": amt,
	  "quantity": "1",
	  "currency": "AED"
	})
	headers = {
	  'Content-Type': 'application/json'
	}
	
	response = requests.request("POST", url, headers=headers, data=payload)
	rdata = json.loads(response.text)
	frappe.errprint(rdata)
	pl = frappe.new_doc("TSC Payment Link")
	pl.requested_date = docu.transaction_date
	pl.document_type = dt
	pl.document_name = docu.name
	pl.status = "Open"
	pl.payment_url = rdata["paymentLink"]
	pl.save(ignore_permissions=True)

	return rdata["paymentLink"]
	
	
	


