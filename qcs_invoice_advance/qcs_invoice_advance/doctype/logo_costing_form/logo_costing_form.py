

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class LogoCostingForm(Document):
	pass


def update_cost():
	cost_doc = frappe.get_all("Logo Costing Form", fields=["name"])
	setup_doc = frappe.get_doc("TSC Logo Setup")
	multiplier = setup_doc.selling_multiplier or 1
	if cost_doc:
		for j in cost_doc:
			cost_doc1 = frappe.get_doc("Logo Costing Form", j.get("name"))
			if cost_doc1.logo_costing_id and cost_doc1.row_name:
				doc = frappe.get_doc("TSC Logo Costing", cost_doc1.logo_costing_id)
				tab = doc.logos
				if (tab):
					for i in range(0, len(tab)):
						if (tab[i].get("name") == cost_doc1.row_name):
							tab[i].logo_unit_cost = cost_doc1.logo_unit_cost
							tab[i].logo_unit_selling = cost_doc1.logo_unit_cost*multiplier
				doc.save(ignore_permissions=True)
	

				
