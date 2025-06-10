

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime
from collections import defaultdict

class LogoCostingForm(Document):
	pass

#improved speed for checking logo cost
def update_cost():
	
	# Preload multiplier once
	setup_doc = frappe.get_doc("TSC Logo Setup")
	multiplier = setup_doc.selling_multiplier or 1

	# Get all Logo Costing Forms that have valid links
	cost_doc = frappe.get_all("Logo Costing Form",
		filters={"logo_costing_id": ["!=", ""], "row_name": ["!=", ""]},
		fields=["name", "logo_costing_id", "row_name", "logo_unit_cost"]
	)

	# Group changes by parent doc
	grouped_updates = defaultdict(list)
	for row in cost_doc:
		grouped_updates[row["logo_costing_id"]].append(row)

	# Only touch each parent doc once
	for parent_id, updates in grouped_updates.items():
		try:
			doc = frappe.get_doc("TSC Logo Costing", parent_id)
			changed = False
			for item in updates:
				for line in doc.logos:
					if line.name == item["row_name"]:
						line.logo_unit_cost = item["logo_unit_cost"]
						line.logo_unit_selling = item["logo_unit_cost"] * multiplier
						changed = True
			if changed:
				doc.save(ignore_permissions=True)
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Logo Costing Update Failed: {parent_id}")
	

				
