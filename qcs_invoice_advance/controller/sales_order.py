
import frappe
import json
import frappe.utils
from frappe.model.mapper import get_mapped_doc
from frappe.utils import add_days, cint, cstr, flt, get_link_to_form, getdate, nowdate, strip_html
from erpnext.stock.get_item_details import get_default_bom, get_price_list_rate
from frappe.model.mapper import get_mapped_doc


@frappe.whitelist()
def create_partial_invoice(sales_order, percentage):
	percentage = json.loads(percentage)
	so = frappe.get_doc("Sales Order", sales_order)
	
	doc = frappe.new_doc("Sales Invoice")
	item = []
	tab = so.items
	for i in range(0, len(tab)):
		qty = tab[i].get("qty")
		per = percentage
		percentage_decimal = per / 100
		balance = percentage_decimal * qty
		# rounded_qty = round(balance)
		
		# so.items[i].invoice_qty = tab[i].get("invoice_qty")+rounded_qty
		
		item.append({
			"custom_ref_no": tab[i].get("custom_ref_no"),
			"item_code": tab[i].get("item_code"),
			"qty": balance,
			"original_qty": tab[i].get("qty"),
			"rate": tab[i].get("rate"),
			"amount": tab[i].get("rate")*balance,
			"original_amount": tab[i].get("amount"),
			"project": tab[i].get("project"),
			"sales_order": sales_order,
			"so_detail": tab[i].get("name")
		})
	doc.update({
		"customer": so.customer,
		"company": so.company,
		"posting_date": so.delivery_date,
		"due_date": so.delivery_date,
		"order_percentage": percentage,
		"items": item,
		"original_total": so.total,
		"taxes_and_charges": so.taxes_and_charges,
		"vat_emirate": so.vat_emirate,
		"project": so.project
	})
	doc.save(ignore_permissions=True)
	so.partial_invoice = so.partial_invoice + percentage
	so.save(ignore_permissions=True)
	frappe.msgprint("Partial Sales Invoice created successfully.")
	return doc.name


def update_payment_link(self, event):
	if (self.custom_quotation):
		doc = frappe.get_all("TSC Payment Link", filters={"document_type":"Quotation", "document_name": self.custom_quotation}, fields=["name"])
		if doc:
			for i in doc:
				payment_doc = frappe.get_doc("TSC Payment Link", i.get("name"))
				payment_doc.sales_order = self.name
				payment_doc.save(ignore_permissions=True)
   
   
   

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
	requested_item_qty = get_requested_item_qty(source_name)

	def get_remaining_qty(so_item):
		return flt(
			flt(so_item.qty)
			- flt(requested_item_qty.get(so_item.name, {}).get("qty"))
			- max(
				flt(so_item.get("delivered_qty"))
				- flt(requested_item_qty.get(so_item.name, {}).get("received_qty")),
				0,
			)
		)

	def update_item(source, target, source_parent):
		# qty is for packed items, because packed items don't have stock_qty field
		target.project = source_parent.project
		target.qty = get_remaining_qty(source)
		target.stock_qty = flt(target.qty) * flt(target.conversion_factor)

		args = target.as_dict().copy()
		args.update(
			{
				"company": source_parent.get("company"),
				"price_list": frappe.db.get_single_value("Buying Settings", "buying_price_list"),
				"currency": source_parent.get("currency"),
				"conversion_rate": source_parent.get("conversion_rate"),
				"custom_sales_order": source_parent.get("name"),
			}
		)

		target.rate = flt(
			get_price_list_rate(args=args, item_doc=frappe.get_cached_doc("Item", target.item_code)).get(
				"price_list_rate"
			)
		)
		target.amount = target.qty * target.rate

	doc = get_mapped_doc(
		"Sales Order",
		source_name,
		{
			"Sales Order": {"doctype": "Material Request", "field_map": {"name": "custom_sales_order"}, "validation": {"docstatus": ["=", 1]}},
			"Packed Item": {
				"doctype": "Material Request Item",
				"field_map": {"parent": "sales_order", "uom": "stock_uom"},
				"postprocess": update_item,
			},
			"Sales Order Item": {
				"doctype": "Material Request Item",
				"field_map": {"name": "sales_order_item", "parent": "sales_order"},
				"condition": lambda item: not frappe.db.exists(
					"Product Bundle", {"name": item.item_code, "disabled": 0}
				)
				and get_remaining_qty(item) > 0,
				"postprocess": update_item,
			},
		},
		target_doc,
	)

	return doc


def get_requested_item_qty(sales_order):
	result = {}
	for d in frappe.db.get_all(
		"Material Request Item",
		filters={"docstatus": 1, "sales_order": sales_order},
		fields=["sales_order_item", "sum(qty) as qty", "sum(received_qty) as received_qty"],
		group_by="sales_order_item",
	):
		result[d.sales_order_item] = frappe._dict({"qty": d.qty, "received_qty": d.received_qty})

	return result


