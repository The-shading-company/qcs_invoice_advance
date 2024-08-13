# Copyright (c) 2024, Quark Cyber Systems FZC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url
import urllib.parse
import json
from jinja2 import Template


class TSCLogoCosting(Document):
	pass

@frappe.whitelist()
def update_logos(logo_tab):
	logo_tab = json.loads(logo_tab)
	doc = frappe.get_doc("TSC Logo Setup")
	tab = doc.table_zrnj
	if len(tab) > 0:
		item = []
		for i in range(0, len(tab)):
			for j in range(0, len(logo_tab)):
				item_dict = {"supplier": tab[i].get("supplier"), "logo_image": logo_tab[j].get("logo_image"), "logo_details": logo_tab[j].get("logo_details")}
				item.append(item_dict)
		return item
	else:
		frappe.throw("Please Fill TSC Logo Setup")
			

@frappe.whitelist()
def make_web_from_link(name):
	logo_doc = frappe.get_doc("TSC Logo Costing", name)
	tab = logo_doc.logos
	for i in range(0, len(tab)):
		site_url = get_url()
		supplier = urllib.parse.quote(tab[i].get("supplier"))
		logo_detail = urllib.parse.quote(tab[i].get("logo_details"))
		row_name = urllib.parse.quote(tab[i].get("name"))
		
		file_doc = frappe.get_doc("File", {"file_url": tab[i].get("logo_image")})
		file_id = file_doc.name
		
		img_link = f'<div class="ql-editor read-mode"><p><img src="{tab[i].get("logo_image")}?fid={file_id}"></p></div>'
		encoded_img_link = urllib.parse.quote(img_link)
		
		link = f"{site_url}/logo-costing/new?logo_costing_id={name}&supplier={supplier}&logo_details={logo_detail}&logo_image={encoded_img_link}&row_name={row_name}"
		tab[i].costing_link = link
  
	logo_doc.save(ignore_permissions=True)
	frappe.msgprint("TSC Logo Costing Web Link Created")


# @frappe.whitelist()
# def send_email_to_supplier(tab, name):
# 	doc = frappe.get_doc("TSC Logo Costing", name)
# 	tab = doc.logos
# 	for i in range(0, len(tab)):
# 		if tab[i].get("supplier") and tab[i].get("sent_email") ==0:
# 			supplier = frappe.get_doc("Supplier", tab[i].get("supplier"))
# 			if supplier.email_id:
# 				supplier_email = supplier.email_id
	
# 				setup_doc = frappe.get_doc("TSC Logo Setup")
# 				if setup_doc.supplier_email_content:
# 					subject = "Logo Costing Form"
# 					message = (setup_doc.supplier_email_content)
# 					frappe.sendmail(
# 						recipients="hiraniyas@gmail.com",
# 						subject=subject,
# 						message=message,
# 						reference_doctype="TSC Logo Costing",
# 						reference_name=name
# 					)

# 					tab[i].sent_email = 1
# 					frappe.msgprint(f"Email sent to {tab[i].get('supplier')}")
# 				else:
# 					subject = "Logo Costing Form"
# 					message = (
# 						f'<div class="ql-editor read-mode">'
# 						f'<p>Dear {tab[i].get("supplier")},</p>'
# 						f'<p><br></p>'
# 						f'<p>We are contacting you regarding the logo costing. We now require an update to the logo costing for the following item:</p>'
# 						f'<p>{tab[i].get("costing_link")}</p>'
# 						f'<p><br></p>'
# 						f'<p>Let us know if you have any questions and I would be happy to assist.</p>'
# 						f'</div>'
# 					)
# 					frappe.sendmail(
# 						recipients="hiraniyas@gmail.com",
# 						subject=subject,
# 						message=message,
# 						reference_doctype="TSC Logo Costing",
# 						reference_name=name
# 					)

# 					tab[i].sent_email = 1
# 					frappe.msgprint(f"Email sent to {tab[i].get('supplier')}")
# 			else:
# 				frappe.msgprint(f"Please Ensure the Supplier Eamil - {tab[i].get('supplier')}")
# 	doc.save(ignore_permissions=True)


from jinja2 import Template

@frappe.whitelist()
def send_email_to_supplier(tab, name):
	doc = frappe.get_doc("TSC Logo Costing", name)
	tab = doc.logos
	for i in range(len(tab)):
		if tab[i].get("supplier") and tab[i].get("sent_email") == 0:
			supplier = frappe.get_doc("Supplier", tab[i].get("supplier"))
			if supplier.email_id:
				supplier_email = supplier.email_id
	
				setup_doc = frappe.get_doc("TSC Logo Setup")
				if setup_doc.supplier_email_content:
					subject = "Logo Costing Form"
					# Render the email content with dynamic data using Jinja templating
					template = Template(setup_doc.supplier_email_content)
					message = template.render(
						supplier=tab[i].get("supplier"),
						costing_link=tab[i].get("costing_link")
					)
					frappe.sendmail(
						recipients=supplier_email,
						subject=subject,
						message=message,
						reference_doctype="TSC Logo Costing",
						reference_name=name
					)

					tab[i].sent_email = 1
					frappe.msgprint(f"Email sent to {tab[i].get('supplier')}")
				else:
					subject = "Logo Costing Form"
					message = (
						f'<div class="ql-editor read-mode">'
						f'<p>Dear {tab[i].get("supplier")},</p>'
						f'<p><br></p>'
						f'<p>We are contacting you regarding the logo costing. We now require an update to the logo costing for the following item:</p>'
						f'<p>{tab[i].get("costing_link")}</p>'
						f'<p><br></p>'
						f'<p>Let us know if you have any questions and I would be happy to assist.</p>'
						f'</div>'
					)
					frappe.sendmail(
						recipients=supplier_email,
						subject=subject,
						message=message,
						reference_doctype="TSC Logo Costing",
						reference_name=name
					)

					tab[i].sent_email = 1
					frappe.msgprint(f"Email sent to {tab[i].get('supplier')}")
			else:
				frappe.msgprint(f"Please ensure the supplier email - {tab[i].get('supplier')}")
	doc.save(ignore_permissions=True)

