import frappe
from frappe.model.mapper import get_mapped_doc
import requests
import json
import math
from frappe import _
from frappe.utils import flt
from frappe.utils.jinja import render_template
from frappe.utils.background_jobs import enqueue
import simplify
import os
from datetime import datetime
import certifi
from frappe.utils import get_system_timezone
from pytz import timezone



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
								#addition from code space
								
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
 
 
def create_shade_sail_price(self, event):
	sh_type = ""
	sw = 0
	sl = 0
	sp = 0
	sc = 0
	sb = 0
	if self.variant_of == "SHA-T":
		for i in self.attributes:
			if i.attribute == "Shade Shape":
				sh_type = i.attribute_value
			if i.attribute == "Shade Width":
				sw = flt(i.attribute_value)
			if i.attribute == "Shade Length":
				sl = flt(i.attribute_value)
			if i.attribute == "Posts":
				sp = flt(i.attribute_value)
			if i.attribute == "Concrete":
				sc = flt(i.attribute_value)
			if i.attribute == "Wall Bracket":
				sb = flt(i.attribute_value)
	if sh_type == "Square":
		f_width = math.ceil(flt(sw) / 3)
		f_qty = f_width * flt(sl)
		f_cost = 25 * f_qty
		s_size = (f_width * 2) + (flt(sl) * 2)
		cable_cost = s_size * 6
		bracket_cost = flt(sb) * 22 * 2
		post_cost = flt(sp) * 380 * 2
		post_pc_cost = flt(sp) * 245 * 2
		post_braket_cost = flt(sp) * bracket_cost * 2
		dshackle_cost = flt(sp) * 5 * 2
		wire_clamp_cost = 2 * 2 * 2
		eyelet_cost = flt(sp) * 18 * 2
		post_cap_cost = flt(sp) * 21 * 2
		stitching_cost = flt(sw) * flt(sl) * 12.5 * 2.1
		installation_cost = 230 * 1.65
		concrete_cost = flt(sc) * 607 * 1.75
		total_price = f_cost + cable_cost + bracket_cost + post_cost + post_pc_cost + post_braket_cost + dshackle_cost + wire_clamp_cost + eyelet_cost + post_cap_cost + stitching_cost + installation_cost + concrete_cost
		if total_price > 0:
			frappe.msgprint("Retail Price List Added")
		if not frappe.db.exists('Item Price', {"item_code": self.name, "price_list": "Retail"}):
			ip_doc = frappe.new_doc("Item Price")
			ip_doc.item_code = self.name
			ip_doc.price_list = "Retail"
			ip_doc.price_list_rate = total_price
			ip_doc.save(ignore_permissions=True)


			

 
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
					org_l = frappe.get_all("File", filters={"file_url":frappe.get_value("Item", att_raw, "image")})
					if len(org_l) > 0:
						org_f = frappe.get_doc("File", org_l[0].name)
						fm = frappe.new_doc("File")
						fm.file_name = org_f.file_name
						fm.file_type = org_f.file_type
						fm.file_url = org_f.file_url
						fm.attached_to_doctype = "Item"
						fm.attached_to_name = self.name
						fm.attached_to_field = "image"
						fm.save()
					


#render jinja template in item desc
# added frame color and fabric color
def set_dynamic_item_description(doc, method):
	if doc.custom_jinja_desc:
		# Prepare your context for the Jinja template. This might include other fields or data as needed.
			context = {
				'doc': doc, 'variants': doc.variants if hasattr(doc, 'variants') else []
				# Include any additional variables or tables you need in your Jinja template.
				# E.g., 'variants': doc.variants if hasattr(doc, 'variants') else []
			}
			
			# Render the description using the custom Jinja template and the context
			rendered_description = render_template(doc.custom_jinja_desc, context)
			
			# Set the rendered description to the item's description field
			doc.description = rendered_description

	if doc.variant_of:
		c_size = ""
		c_color = ""
		for v in doc.attributes:
			if v.attribute == "Fabric Color":
				c_color = v.attribute_value
			if v.attribute == "Frame Color":
				c_color = v.attribute_value
			if v.attribute == "Size":
				c_size = v.attribute_value
				if 'x' in c_size:
					part1, part2 = c_size.split('x')
					value1 = int(float(part1) * 100)
					value2 = int(float(part2) * 100)
					doc.custom_tsc_size = str(value1) + " x " + str(value2)
				else:
					doc.custom_tsc_size = c_size
		if not doc.custom_tsc_color:
			doc.custom_tsc_color = c_color


def add_sale_price(self, event):

	itemprice = frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Retail"})

	if frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": "Retail"}):
		for i in itemprice:
			ip_doc = frappe.get_doc("Item Price", i)
			ip_doc.price_list_rate = self.total_cost * 2.25
			ip_doc.save(ignore_permissions=True)
	else:
		ip_doc = frappe.new_doc("Item Price")
		ip_doc.item_code = self.item
		ip_doc.price_list = "Retail"
		ip_doc.price_list_rate = self.total_cost * 2.25
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
			ip_doc.price_list_rate = self.total_cost * 1.8
			ip_doc.save(ignore_permissions=True)
	else:
		ip_doc = frappe.new_doc("Item Price")
		ip_doc.item_code = self.item
		ip_doc.price_list = "Dealer"
		ip_doc.price_list_rate = self.total_cost * 1.8
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

#This script adds margins for quotation. Iterates through the line items and updated either from bom or from item cost.
def add_margins(self, event):
	total_cost = 0
	total_cost_with_qty = 0
	total_margin = 0
	total_margin_with_qty = 0
	for item in self.items:
		bom = frappe.get_all("BOM", filters={"item": item.item_code, "is_active": 1, "is_default": 1})
		if len(bom) > 0:
			bom_index = frappe.get_doc("BOM", bom[0].name)
			item.custom_tsc_cost = bom_index.total_cost
			item.custom_tsc_cost_with_qty = bom_index.total_cost * item.qty
			total_cost += item.custom_tsc_cost
			total_cost_with_qty += item.custom_tsc_cost_with_qty
		else:
			item.custom_tsc_cost = item.valuation_rate
			item.custom_tsc_cost_with_qty = item.valuation_rate * item.qty
			total_cost += item.custom_tsc_cost
			total_cost_with_qty += item.custom_tsc_cost_with_qty
   
		if item.custom_tsc_cost > 0:
			item.custom_tsc_margin = item.rate - item.custom_tsc_cost
			total_margin += item.custom_tsc_margin
			with_qty_margin = item.rate - item.custom_tsc_cost_with_qty
			total_margin_with_qty += with_qty_margin
   
			if item.custom_tsc_margin > 0:
				item.custom_tsc_margin_per = (item.custom_tsc_margin * 100) / item.custom_tsc_cost

	self.custom_total_cost = total_cost_with_qty
	if self.custom_total_cost > 0 and total_cost_with_qty > 0:
		self.custom_total_margin = self.net_total - total_cost_with_qty
		self.custom_margin_percent = (self.custom_total_margin * 100) / self.custom_total_cost

@frappe.whitelist()
def recalculate_sales_order_margins(sales_order):
    doc = frappe.get_doc("Sales Order", sales_order)
    from qcs_invoice_advance.controller.item import add_margins_sales_order
    add_margins_sales_order(doc, None)
    doc.save(ignore_permissions=True)

#this adds margin to sales orders just like the script above for quotations.
def add_margins_sales_order(doc, event):
    total_cost = 0
    total_cost_with_qty = 0
    total_margin = 0
    total_margin_with_qty = 0

    for item in doc.items:
        bom = frappe.get_all("BOM", filters={"item": item.item_code, "is_active": 1, "is_default": 1})
        if bom:
            bom_index = frappe.get_doc("BOM", bom[0].name)
            item.custom_tsc_cost = bom_index.total_cost
            item.custom_tsc_cost_with_qty = bom_index.total_cost * item.qty
            total_cost = total_cost + item.custom_tsc_cost
            total_cost_with_qty = total_cost_with_qty + item.custom_tsc_cost_with_qty
        else:
            item.custom_tsc_cost = item.valuation_rate
            item.custom_tsc_cost_with_qty = item.valuation_rate * item.qty
            total_cost = total_cost + item.custom_tsc_cost
            total_cost_with_qty = total_cost_with_qty + item.custom_tsc_cost_with_qty

        if item.custom_tsc_cost > 0:
            item.custom_tsc_margin = item.rate - item.custom_tsc_cost
            total_margin = total_margin + item.custom_tsc_margin
            with_qty_margin = item.rate - item.custom_tsc_cost_with_qty
            total_margin_with_qty = total_margin_with_qty + with_qty_margin

            if item.custom_tsc_margin > 0:
                item.custom_tsc_margin_per = (item.custom_tsc_margin * 100) / item.custom_tsc_cost

    doc.custom_total_cost = total_cost_with_qty
    if doc.custom_total_cost > 0 and total_cost_with_qty > 0:
        doc.custom_total_margin = doc.net_total - total_cost_with_qty
        doc.custom_margin_percent = (doc.custom_total_margin * 100) / doc.custom_total_cost

def add_quote_link(self, event):
	if self.custom_tsc_site_visit:
		sv = frappe.get_doc("TSC Site Visit", self.custom_tsc_site_visit)
		sv.quotation = self.name
		sv.status = "Quoting"
		sv.save(ignore_permissions=True)
  
def update_service_call(self, event):
	if self.custom_tsc_service_call:
		doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
		doc.quote = self.name
		doc.status = "Quoting"
		doc.save(ignore_permissions=True)
  
def update_service_call_sales_order(self, event):
	if self.custom_tsc_service_call:
		doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
		doc.sales_order = self.name
		doc.save(ignore_permissions=True)
  
def update_purchase_to_sales(self, event):
	if self.custom_sales_order:
		doc = frappe.get_doc("Sales Order", self.custom_sales_order)
		doc.custom_purchase_order = self.name
		doc.save(ignore_permissions=True)


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


# @frappe.whitelist()
# def make_warranty_claim(source_name, target_doc=None):
# 	doclist = get_mapped_doc(
# 		"TSC Service Call",
# 		source_name,
# 		{
# 			"TSC Service Call": {
# 				"doctype": "Warranty Claim",
# 				"field_map": {"customer": "customer", "issue_log_date": "complaint_date", "address": "service_address", "mob_no": "contact_mobile", "issue_details": "complaint"},
# 			},
			
# 		},
# 		target_doc,
		
# 	)

# 	return doclist


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
			cont.is_primary_contact = 1
			cont.save(ignore_permissions=True)
		if sv.address:
			address = frappe.new_doc("Address")
			address.address_title = sv.customer_name
			address.address_type = "Billing"
			address.address_line1 = sv.address
			address.country = "United Arab Emirates"
			address.is_primary_address = 1
			address.city = sv.territory
			address.append("links",{
				"link_doctype": "Customer",
				"link_name": cust.name
			})
			address.save(ignore_permissions=True)
	else:
		# pass
		frappe.throw("Quatation Created Already for this Customer. So No Need to Create!")
		# frappe.throw(title='Error', msg='Same Customer Name exists, please differentiate!')
			
		
		
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
def make_warranty_claim(source_name, target_doc=None):
	sv = frappe.get_doc("TSC Service Call", source_name)
	doclist = get_mapped_doc(
			"TSC Service Call",
			source_name,
			{
				
				"TSC Service Call": {
					"doctype": "Warranty Claim",
					"field_map": {"customer": "customer", "issue_details":"complaint", "name":"custom_service_call", "sales_order": "custom_sales_order_name"},
				},
			
			},
			target_doc,
		)
	return doclist


def warrenty_claim_sales_order(self, event):
	if (self.custom_sales_order_name):
		if (self.custom_sales_order):
			pass
		else:
			sales_order = frappe.get_doc("Sales Order", self.custom_sales_order_name)
			if (sales_order):
				self.custom_sales_order = sales_order.name


@frappe.whitelist()
def get_contact_query(customer):
	# return customer
	customer1 = customer
	if not customer1:
		return []

	return frappe.db.sql("""
		SELECT 
			contact.name
		FROM 
			`tabContact` contact
		JOIN 
			`tabDynamic Link` links ON links.parent = contact.name
		WHERE 
			links.link_doctype = 'Customer' AND links.link_name = %s
	""", (customer1))


@frappe.whitelist()
def create_sub_po(dt, dn, parent_item, can_item, qty, uom, line_id, supplier):
	c_type = ""
	c_size = ""
	c_model = ""
	c_cost = 0
	c_cut_size = 0
	c_motor = ""
	p_item = frappe.get_doc("Item", parent_item)
	for v in p_item.attributes:
		if v.attribute == "Canopy Type":
			c_type = v.attribute_value
		if v.attribute == "Size":
			c_size = v.attribute_value
		if v.attribute == "Model":
			c_model = v.attribute_value
		if v.attribute == "Motor":
			c_motor = v.attribute_value
	if c_type != "" and c_size != "":
		c_cost = frappe.db.get_value("TSC Stitching table", {"canopy_type":c_type, "canopy_size":c_size}, "no_flap_stitching_cost")
	if c_model != "" and c_motor == "Somfy":
		c_cut_size = frappe.db.get_value("Item Attribute Value", {"parent":"Model", "attribute_value":c_model}, "custom_motor_cut")
	if c_model != "" and c_motor != "Somfy":
		c_cut_size = frappe.db.get_value("Item Attribute Value", {"parent":"Model", "attribute_value":c_model}, "custom_manual_cut")
	
	
	so = frappe.get_doc("Sales Order", dn)
	po = frappe.new_doc("Purchase Order")
	po.company = so.company
	po.is_subcontracted = 1
	po.transaction_date = so.transaction_date
	po.supplier = supplier
	po.schedule_date = so.delivery_date
	part1, part2 = c_size.split('x')
	value1 = int(float(part1) * 100)
	value2 = int(float(part2) * 100)
	po.append("items",{
		"fg_item": can_item,
		"fg_item_qty": qty,
		"item_code": "Stitching",
		"qty": qty,
		"description": "Stitching for awning " + c_model + ". Cut Size: " + str(value1 - c_cut_size) + " x " + str(value2 - 30),
		"uom": uom,
		"rate": c_cost,
		"schedule_date": so.delivery_date,
		"sales_order": so.name,
		"sales_order_item": line_id
	})
	po.taxes_and_charges = "UAE VAT 5% - TSUTCL"
	po.run_method("set_missing_values")
	po.run_method("calculate_taxes_and_totals")
	po.save()
	return po




def update_item_price_based_on_bom():
	# Fetch all Item Prices where the item has a BOM and belongs to the "Retail" Price List
	item_prices = frappe.get_all("Item Price", filters={
		'price_list': 'Retail',
		'item_code': ['in', get_items_with_latest_bom()]
	}, fields=["name", "item_code"])

	for item_price in item_prices:
		bom_name = frappe.get_value("BOM", {"item": item_price.item_code, "is_default": 1, "docstatus": 1}, "name", order_by="creation desc")
		if bom_name:
			bom = frappe.get_doc("BOM", bom_name)
			bom.update_cost()
			bom.save()
			


	frappe.db.commit()  # Commit changes to the database

def get_items_with_latest_bom():
	"""Helper function to get item codes that have an associated latest BOM."""
	# Fetch all BOMs that are not cancelled and order them by item and creation date
	boms = frappe.get_all("BOM", fields=["item", "name", "creation"], filters={'docstatus': 1}, order_by="item, creation desc")
	
	latest_boms = {}
	for bom in boms:
		if bom['item'] not in latest_boms:
			latest_boms[bom['item']] = bom['name']  # Assumes the first BOM for each item is the latest due to sorting
	
	return list(latest_boms.keys())

#updated run_retail_price from items that have a bom
@frappe.whitelist()
def run_retail_update():
	# Execute the function
	enqueue(update_item_price_based_on_bom, queue='long', timeout=6000, is_async=True, job_name='update_item_price_based_on_bom')
	return "Started"


## This is a cron which loops through all products and updated the Custom_average_cost in Item with the Average Cost from the stock ledger  
@frappe.whitelist()
def cron_update_item_average_rate():
	all_item_doc = frappe.get_all("Item", filters={"disabled":0}, fields=["name"])
	if (all_item_doc):
		batch_size = 50  # Adjust batch size based on performance
		for i in range(0, len(all_item_doc), batch_size):
			batch = all_item_doc[i:i + batch_size]
			enqueue(process_batch, items=batch)
			# for i in all_item_doc:
		# 	doc = frappe.get_doc("Item", i.get("name"))
		# 	valuation_rate = frappe.db.sql("""
		# 		SELECT valuation_rate
		# 		FROM `tabStock Ledger Entry`
		# 		WHERE item_code = %s
		# 		ORDER BY posting_date DESC, posting_time DESC
		# 		LIMIT 1
		# 	""", i.get("name"))
		# 	valuation_rate = valuation_rate[0][0] if valuation_rate else 0

		# 	if valuation_rate:
		# 		doc.custom_average_cost = valuation_rate
		# 	else:
		# 		doc.custom_average_cost = 0
		# 	doc.save(ignore_permissions=True)
  
def process_batch(items):
	for i in items:
		doc = frappe.get_doc("Item", i.get("name"))
		valuation_rate = frappe.db.sql("""
			SELECT valuation_rate
			FROM `tabStock Ledger Entry`
			WHERE item_code = %s
			ORDER BY posting_date DESC, posting_time DESC
			LIMIT 1
		""", i.get("name"))
		valuation_rate = valuation_rate[0][0] if valuation_rate else 0

		doc.custom_average_cost = valuation_rate or 0
		doc.save(ignore_permissions=True)
   

def epoch_time_ms_to_datetime(epoch_time_ms):
    system_timezone = timezone(get_system_timezone())
    epoch_time = epoch_time_ms / 1000.0
    converted_datetime = datetime.fromtimestamp(epoch_time)
    converted_datetime_in_timezone = converted_datetime.astimezone(system_timezone)
    formatted_datetime = converted_datetime_in_timezone.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime
