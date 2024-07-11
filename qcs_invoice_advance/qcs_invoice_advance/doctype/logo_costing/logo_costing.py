# Copyright (c) 2024, Quark Cyber Systems FZC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url
import urllib.parse



class LogoCosting(Document):
	pass


@frappe.whitelist()
def make_web_from_link(name):
	logo_doc = frappe.get_doc("Logo Costing", name)
	tab = logo_doc.logos
	for i in range(0, len(tab)):
		site_url = get_url()
		supplier = urllib.parse.quote(tab[i].get("supplier"))
		logo_detail = urllib.parse.quote(tab[i].get("logo_details"))
		row_name = urllib.parse.quote(tab[i].get("name"))
		
		file_doc = frappe.get_doc("File", {"file_url": tab[i].get("logo_image")})
		file_id = file_doc.name
		frappe.errprint(file_id)
		
		img_link = f'<div class="ql-editor read-mode"><p><img src="{tab[i].get("logo_image")}?fid={file_id}"></p></div>'
		encoded_img_link = urllib.parse.quote(img_link)
		
		link = f"{site_url}/logo-costing/new?logo_costing_id={name}&supplier={supplier}&logo_details={logo_detail}&logo_image={encoded_img_link}&row_name={row_name}"
		tab[i].costing_link = link
  
	logo_doc.save(ignore_permissions=True)
	frappe.msgprint("Logo Costing Web Link Created")
