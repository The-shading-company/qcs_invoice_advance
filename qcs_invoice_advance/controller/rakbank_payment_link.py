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
 
# get payment Invoice

	payment_link = rdata["paymentLink"]
	payment_id = payment_link.split('/')[-1]
	rakbank_api_settings = frappe.get_doc("Rakbank API Settings")
	if (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
 
		simplify.public_key = rakbank_api_settings.public_key
		simplify.private_key = rakbank_api_settings.private_key
		os.environ['SSL_CERT_FILE'] = certifi.where()
		invoice = simplify.Invoice.find(payment_id)
		frappe.errprint(invoice)
		invoice_id = invoice["id"]
	
		pl = frappe.new_doc("TSC Payment Link")
		pl.requested_date = docu.transaction_date
		pl.document_type = dt
		pl.document_name = docu.name
		pl.customer = getattr(docu, "party_name", None) or getattr(docu, "customer", None)
		  
		if dt == "Quotation":
			doc = frappe.get_all("Sales Order", filters={"custom_quotation": docu.name}, fields=["name"])
			if doc:
				so_list = []
				for i in doc:
					so_list.append(i.get("name"))
				pl.sales_order = so_list[0]
				pl.link_sales_order = so_list[0]
		
		pl.status = "Open"
		pl.payment_url = rdata["paymentLink"]
		pl.payment_invoice = invoice_id
		pl.save(ignore_permissions=True)
	
		quo_doc = frappe.get_doc("Quotation", docu.name)
		quo_doc.custom_tsc_payment_link = pl.name
		quo_doc.save(ignore_permissions=True)
	
		return rdata["paymentLink"]
	else:
		frappe.throw("Somthing Missing in Rakbank API Settings")

def update_tsc_payment_link(self, event):
	if (self.custom_tsc_payment_link):
		payment_link = frappe.get_doc("TSC Payment Link", self.custom_tsc_payment_link)
		payment_link.document_name = self.name
		payment_link.save(ignore_permissions=True)  

# duplicate commented out
"""  
@frappe.whitelist()
def create_payment_link1(dt, dn, amt, purpose):
	frappe.errprint("jjjjj")
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
 
# get payment Invoice

	payment_link = rdata["paymentLink"]
	payment_id = payment_link.split('/')[-1]
	rakbank_api_settings = frappe.get_doc("Rakbank API Settings")
	if (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
 
		simplify.public_key = rakbank_api_settings.public_key
		simplify.private_key = rakbank_api_settings.private_key
		os.environ['SSL_CERT_FILE'] = certifi.where()
		invoice = simplify.Invoice.find(payment_id)
		frappe.errprint(invoice)
		invoice_id = invoice["id"]
	
		pl = frappe.new_doc("TSC Payment Link")
		pl.requested_date = docu.transaction_date
		if dt=="Quotation":
			pl.quotation = dn
		if dt=="Sales Order":
			pl.link_sales_order = dn
		pl.document_type = dt
		pl.document_name = docu.name
		pl.customer = docu.customer
		pl.sales_order = docu.name
		pl.status = "Open"
		pl.payment_url = rdata["paymentLink"]
		pl.payment_invoice = invoice_id
		pl.save(ignore_permissions=True)
  
		return rdata["paymentLink"]

	else:
		frappe.throw("Something Missing in Rakbank API Settings")
		
"""
# This is an improved version which handles sales orders and quotations. Uses Echt Microservice

@frappe.whitelist()
def create_payment_link2(dt, dn, amt, purpose):
	import requests, json, certifi, os
	from simplify import simplify

	docu = frappe.get_doc(dt, dn)
	url = "https://simplify-rak-gbermhh3pa-uc.a.run.app/create"

	payload = json.dumps({
		"key": "kl8EvdFF4EPPIo5JHJto74lz-EOt5rabkmnE",
		"reference": dn,
		"note": "test",
		"dueDate": str(docu.get("transaction_date")),
		"memo": "Delivery To",
		"name": docu.get("customer_name"),
		"email": docu.get("contact_email") or "",
		"description": purpose,
		"amount": amt,
		"quantity": "1",
		"currency": "AED"
	})

	headers = {
		'Content-Type': 'application/json'
	}

	response = requests.post(url, headers=headers, data=payload)
	rdata = json.loads(response.text)
	frappe.errprint(rdata)

	payment_link = rdata.get("paymentLink")
	if not payment_link:
		frappe.throw("No payment link returned from Rakbank")

	payment_id = payment_link.split('/')[-1]

	rakbank_api_settings = frappe.get_doc("Rakbank API Settings")
	if not (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
		frappe.throw("Rakbank API credentials are missing")

	simplify.public_key = rakbank_api_settings.public_key
	simplify.private_key = rakbank_api_settings.private_key
	os.environ['SSL_CERT_FILE'] = certifi.where()

	invoice = simplify.Invoice.find(payment_id)
	frappe.errprint(invoice)

	invoice_id = invoice.get("id")

	pl = frappe.new_doc("TSC Payment Link")
	pl.requested_date = docu.get("transaction_date")
	pl.document_type = dt
	pl.document_name = dn
	pl.customer = docu.get("customer")
	pl.status = "Open"
	pl.payment_url = payment_link
	pl.payment_invoice = invoice_id

	if dt == "Quotation":
		pl.quotation = dn
	if dt == "Sales Order":
		pl.link_sales_order = dn
		pl.sales_order = dn  # keep if needed by reports/scripts

	pl.save(ignore_permissions=True)

	return payment_link


# This version is a direct to rakbank api request not using Echt Microservice. For Testing.

@frappe.whitelist()
def create_payment_link3(dt, dn, amt, purpose):
	import simplify, os, certifi
	from datetime import datetime

	docu = frappe.get_doc(dt, dn)
	rakbank_api_settings = frappe.get_doc("Rakbank API Settings")

	if not (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
		frappe.throw("Rakbank API keys are missing in Rakbank API Settings")

	simplify.public_key = rakbank_api_settings.public_key
	simplify.private_key = rakbank_api_settings.private_key
	os.environ['SSL_CERT_FILE'] = certifi.where()

	email = getattr(docu, "contact_email", "") or "sales@theshadingcompany.ae"
	send_email = email != "sales@theshadingcompany.ae"

	try:
		invoice = simplify.Invoice.create({
			"reference": dn,
			"note": "test",
			"name": getattr(docu, "customer_name", None),
			"memo": "Delivery To",
			"currency": "AED",
			"dueDate": str(docu.get("transaction_date")),
			"items": [{
				"amount": int(float(amt) * 100),  # convert AED to fils
				"quantity": 1,
				"description": purpose
			}],
			"email": email
		})
	except Exception as e:
		frappe.log_error(str(e), "Rakbank Invoice Creation Error")
		frappe.throw("Error while creating invoice with Rakbank API")

	try:
		invoice["status"] = "OPEN"
		if send_email:
			invoice["sendMail"] = True
		invoice.update()
	except Exception as e:
		frappe.log_error(str(e), "Rakbank Invoice Update Error")
		frappe.throw("Invoice created but failed to update with Rakbank")

	payment_link = f"https://rakbank.simplify.com/invoicing/pay/#/{simplify.public_key}/id/{invoice['uuid']}"

	# Save in TSC Payment Link
	pl = frappe.new_doc("TSC Payment Link")
	pl.requested_date = docu.get("transaction_date")
	if dt == "Quotation":
		pl.quotation = dn
	elif dt == "Sales Order":
		pl.link_sales_order = dn
	pl.document_type = dt
	pl.document_name = docu.name
	pl.customer = getattr(docu, "customer", None) or getattr(docu, "customer_name", None)
	pl.sales_order = docu.name
	pl.status = "Open"
	pl.payment_url = payment_link
	pl.payment_invoice = invoice["id"]
	pl.save(ignore_permissions=True)

	return payment_link

## Cron which checks for paid payment links

@frappe.whitelist()
def cron_rakbank_api():
	batch_size = 25  # Adjust batch size to your server's capacity

	all_payment = frappe.get_all("TSC Payment Link", filters={
		"status": ["!=", "Cancelled"],
		"payment_status": ["!=", "PAID"]
	}, fields=["name"])

	if not all_payment:
		return

	for i in range(0, len(all_payment), batch_size):
		batch = all_payment[i:i + batch_size]
		enqueue(process_rakbank_batch, queue='long', timeout=300, items=batch)

def process_rakbank_batch(items):
	settings = frappe.get_cached_doc("Rakbank API Settings")

	if not (settings.public_key and settings.private_key):
		frappe.log_error("Missing Rakbank API keys", "Rakbank Sync")
		return

	simplify.public_key = settings.public_key
	simplify.private_key = settings.private_key
	os.environ['SSL_CERT_FILE'] = certifi.where()

	for row in items:
		try:
			doc = frappe.get_doc("TSC Payment Link", row.name)
			if not doc.payment_url:
				continue

			payment_id = doc.payment_url.split('/')[-1]
			payment = simplify.Invoice.find(payment_id)

			status = payment.get("status")
			doc.payment_status = status
			doc.payment_invoice = payment.get("id")

			if status == "PAID":
				if payment.get("datePaid"):
					doc.paid_date = epoch_time_ms_to_datetime(payment["datePaid"])
				if payment.get("payment"):
					doc.paid_amount = payment["payment"]["amount"] / 100

			doc.save(ignore_permissions=True)

		except Exception as e:
			frappe.log_error(frappe.get_traceback(), f"Rakbank Payment Sync Failed: {row.name}")


def epoch_time_ms_to_datetime(epoch_time_ms):
    system_timezone = timezone(get_system_timezone())
    epoch_time = epoch_time_ms / 1000.0
    converted_datetime = datetime.fromtimestamp(epoch_time)
    converted_datetime_in_timezone = converted_datetime.astimezone(system_timezone)
    formatted_datetime = converted_datetime_in_timezone.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime
