# Copyright (c) 2024, Quark Cyber Systems FZC and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class LogoCostingForm(Document):
	pass
	# def after_insert(self):
	# 	frappe.errprint("kkkkk")
	# 	if self.logo_costing_id and self.row_name:
	# 		doc = frappe.get_doc("Logo Costing", self.logo_costing_id)
	# 		tab = doc.logos
	# 		if (tab):
	# 			for i in range(0, len(tab)):
	# 				if (tab[i].get("name") == self.row_name):
	# 					frappe.errprint(tab[i].get("name"))
	# 					frappe.errprint(self.logo_unit_cost)
	# 					tab[i].logo_unit_cost = self.logo_unit_cost
	# 		doc.save(ignore_permissions=True)
 
def update_cost():
	cost_doc = frappe.get_all("Logo Costing Form", fields=["name"])
	if cost_doc:
		for j in cost_doc:
			cost_doc1 = frappe.get_doc("Logo Costing Form", j.get("name"))
			if cost_doc1.logo_costing_id and cost_doc1.row_name:
				doc = frappe.get_doc("TSC Logo Costing", cost_doc1.logo_costing_id)
				tab = doc.logos
				if (tab):
					for i in range(0, len(tab)):
						if (tab[i].get("name") == cost_doc1.row_name):
							frappe.errprint(tab[i].get("name"))
							frappe.errprint(cost_doc1.logo_unit_cost)
							tab[i].logo_unit_cost = cost_doc1.logo_unit_cost
				doc.save(ignore_permissions=True)
	
				
				
