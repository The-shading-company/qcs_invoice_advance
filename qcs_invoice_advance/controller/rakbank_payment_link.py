import frappe
import os
import math
import certifi
import simplify
import requests  # Required if calling external APIs (like Rakbank auth)
from frappe import _
from frappe.utils import get_system_timezone
from frappe.utils.background_jobs import enqueue
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Only needed if you're converting timezones

#@frappe.whitelist()
# def create_payment_link(dt, dn, amt, purpose):
#     docu = frappe.get_doc(dt, dn)
#     url = "https://simplify-rak-gbermhh3pa-uc.a.run.app/create"

#     payload = json.dumps({
#       "key": "kl8EvdFF4EPPIo5JHJto74lz-EOt5rabkmnE",
#       "reference": dn,
#       "note": "test",
#       "dueDate": str(docu.transaction_date),
#       "memo": "Delivery To",
#       "name": docu.customer_name,
#       "email": docu.contact_email if docu.contact_email else "",
#       "description": purpose,
#       "amount": amt,
#       "quantity": "1",
#       "currency": "AED"
#     })
#     headers = {
#       'Content-Type': 'application/json'
#     }
    
#     response = requests.request("POST", url, headers=headers, data=payload)
#     rdata = json.loads(response.text)
#     frappe.errprint(rdata)
 
# # get payment Invoice

#     payment_link = rdata["paymentLink"]
#     payment_id = payment_link.split('/')[-1]
#     rakbank_api_settings = frappe.get_doc("Rakbank API Settings")
#     if (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
 
#         simplify.public_key = rakbank_api_settings.public_key
#         simplify.private_key = rakbank_api_settings.private_key
#         os.environ['SSL_CERT_FILE'] = certifi.where()
#         invoice = simplify.Invoice.find(payment_id)
#         frappe.errprint(invoice)
#         invoice_id = invoice["id"]
    
#         pl = frappe.new_doc("TSC Payment Link")
#         pl.requested_date = docu.transaction_date
#         pl.document_type = dt
#         pl.document_name = docu.name
#         pl.customer = getattr(docu, "party_name", None) or getattr(docu, "customer", None)
          
#         if dt == "Quotation":
#             doc = frappe.get_all("Sales Order", filters={"custom_quotation": docu.name}, fields=["name"])
#             if doc:
#                 so_list = []
#                 for i in doc:
#                     so_list.append(i.get("name"))
#                 pl.sales_order = so_list[0]
#                 pl.link_sales_order = so_list[0]
        
#         pl.status = "Open"
#         pl.payment_url = rdata["paymentLink"]
#         pl.payment_invoice = invoice_id
#         pl.save(ignore_permissions=True)
    
#         quo_doc = frappe.get_doc("Quotation", docu.name)
#         quo_doc.custom_tsc_payment_link = pl.name
#         quo_doc.save(ignore_permissions=True)
    
#         return rdata["paymentLink"]
#     else:
#         frappe.throw("Somthing Missing in Rakbank API Settings")


#this calls the quotation payment link update. im not sure this is needed. we should be directly updating in the tsc payment link link field.
def update_tsc_payment_link(self, event):
    if (self.custom_tsc_payment_link):
        payment_link = frappe.get_doc("TSC Payment Link", self.custom_tsc_payment_link)
        payment_link.document_name = self.name
        payment_link.save(ignore_permissions=True)  


# ─────────────────────────────────────────────────────────────────────────────
# The Shading Umbrella Trading Co LLC - RakBank
# ─────────────────────────────────────────────────────────────────────────────
@frappe.whitelist()
def create_payment_link3(dt, dn, amt, purpose):
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
            "memo": purpose,
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
    pl.custom_source = "Rakbank"
    pl.custom_company = "The Shading Umbrella Trading Co LLC"
    pl.save(ignore_permissions=True)

    return payment_link


# ─────────────────────────────────────────────────────────────────────────────
# Helper: epoch-milliseconds  → timezone-aware datetime
# ─────────────────────────────────────────────────────────────────────────────
def epoch_time_ms_to_datetime(ms: int) -> datetime:
    """Convert epoch milliseconds to a timezone-aware datetime in system TZ."""
    tz = ZoneInfo(get_system_timezone())
    return datetime.fromtimestamp(ms / 1000.0, tz)

# ─────────────────────────────────────────────────────────────────────────────
# Cron: check Rakbank payment links (all inline, no batching yet)
# ─────────────────────────────────────────────────────────────────────────────
import pprint  # <-- pretty-prints dicts for easier reading

@frappe.whitelist()
def cron_rakbank_api():
    """
    Check all open Rakbank payment links and update their status.
    """
    links = frappe.get_all(
        "TSC Payment Link",
        filters={
            "status": ["!=", "Cancelled"],
            "payment_status": ["!=", "PAID"],
            "custom_company": "The Shading Umbrella Trading Co LLC",
            "custom_source": "Rakbank"
        },
        fields=["name", "payment_url"]
    )

    if not links:
        frappe.logger().info("Rakbank cron: nothing to check")
        return

    # API key setup
    keys = frappe.get_cached_doc("Rakbank API Settings")
    simplify.public_key = keys.public_key
    simplify.private_key = keys.private_key
    os.environ["SSL_CERT_FILE"] = certifi.where()

    for row in links:
        name = row.name
        try:
            if not row.payment_url:
                continue

            payment_id = row.payment_url.rsplit("/", 1)[-1]
            payment = simplify.Invoice.find(payment_id).to_dict()

            frappe.logger().info(f"Checked {name} → {payment['status']}")

            doc = frappe.get_doc("TSC Payment Link", name)
            doc.payment_status = payment["status"]
            doc.payment_invoice = payment["id"]

            if payment["status"] == "PAID":
                if payment.get("datePaid"):
                    doc.paid_date = epoch_time_ms_to_datetime(payment["datePaid"]).replace(tzinfo=None)
                if payment.get("payment"):
                    doc.paid_amount = payment["payment"]["amount"] / 100

            doc.save(ignore_permissions=True)

        except Exception:
            frappe.log_error(frappe.get_traceback(), f"Rakbank cron failed for {name}")
            continue

    frappe.db.commit()

def process_batch1(items):
    keys = frappe.get_cached_doc("Rakbank API Settings")
    simplify.public_key  = keys.public_key
    simplify.private_key = keys.private_key
    os.environ["SSL_CERT_FILE"] = certifi.where()

    to_update, errors = [], []

    for row in items:
        try:
            doc = frappe.get_doc("TSC Payment Link", row["name"])
            if not doc.payment_url or doc.payment_status in ("PAID", "CANCELLED"):
                continue

            payment_id = doc.payment_url.rsplit('/', 1)[-1]
            payment    = simplify.Invoice.find(payment_id).to_dict()

            updates = {
                "payment_status":  payment["status"],
                "payment_invoice": payment["id"],
            }

            if payment["status"] == "PAID":
                if payment.get("datePaid"):
                    updates["paid_date"] = epoch_time_ms_to_datetime(
                        payment["datePaid"]).replace(tzinfo=None)
                if payment.get("payment"):
                    updates["paid_amount"] = payment["payment"]["amount"] / 100

            to_update.append((updates, doc.name))

        except Exception:
            errors.append(frappe.get_traceback())

    # bulk DB write
    for upd, name in to_update:
        frappe.db.set_value("TSC Payment Link", name, upd, update_modified=False)
    frappe.db.commit()

    if errors:
        frappe.log_error("\n\n".join(errors[:10]), "Rakbank Batch Errors")

# ---------------------------------------------------------------------------
# BATCH-FRIENDLY WRAPPER  ➜  bench execute "qcs_invoice_advance.controller.rakbank_payment_link.cron_rakbank_api_batch"
# ---------------------------------------------------------------------------
@frappe.whitelist()
def cron_rakbank_api_batch(test_inline: bool = False, batch_size: int = 40):
    """Slice open Rakbank links into batches and process or enqueue them."""
    names = frappe.get_all(
        "TSC Payment Link",
        filters={
            "status": ["!=", "Cancelled"],
            "payment_status": ["!=", "PAID"],
            "custom_company": "The Shading Umbrella Trading Co LLC",
            "custom_source": "Rakbank"
        },
        pluck="name"
    )

    if not names:
        frappe.logger().info("Rakbank batch cron: nothing to check")
        return

    for i in range(0, len(names), batch_size):
        batch = [{"name": n} for n in names[i : i + batch_size]]

        if test_inline:
            frappe.logger().info(f"▶ Running batch inline ({i}-{i+len(batch)-1})")
            process_batch1(batch)
            frappe.db.commit()
        else:
            enqueue(
                "qcs_invoice_advance.controller.rakbank_payment_link.process_batch1",
                queue="long",
                timeout=300,
                items=batch,
            )

    if not test_inline:
        total_batches = math.ceil(len(names) / batch_size)
        frappe.logger().info(f"✅ Enqueued {len(names)} links in {total_batches} batches")


# ─────────────────────────────────────────────────────────────────────────────
# Cron: Cancels old Payment Links 1 per week - older than 90 days
# ─────────────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def cancel_old_open_payment_links():
    cutoff_date = frappe.utils.now_datetime() - timedelta(days=90)

    old_links = frappe.get_all(
        "TSC Payment Link",
        filters={
            "status": "Open",
            "custom_company": "The Shading Umbrella Trading Co LLC",
            "custom_source": "Rakbank",
            "payment_status": "OPEN"
        },
        fields=["name", "payment_url", "creation"]
    )

    rakbank_api_settings = frappe.get_doc("Rakbank API Settings")
    if not (rakbank_api_settings.public_key and rakbank_api_settings.private_key):
        frappe.throw("Rakbank API keys are not configured.")

    simplify.public_key = rakbank_api_settings.public_key
    simplify.private_key = rakbank_api_settings.private_key
    os.environ["SSL_CERT_FILE"] = certifi.where()

    cancelled_links = []

    for entry in old_links:
        try:
            if entry.creation and entry.creation < cutoff_date:
                doc = frappe.get_doc("TSC Payment Link", entry.name)

                if not doc.payment_url:
                    continue

                payment_id = doc.payment_url.split("/")[-1]
                invoice = simplify.Invoice.find(payment_id)

                if invoice and invoice["status"] == "OPEN":
                    invoice["status"] = "CANCELLED"
                    invoice.update()

                    doc.status = "Cancelled"
                    doc.payment_status = "CANCELLED"
                    doc.save(ignore_permissions=True)

                    cancelled_links.append({
                        "name": doc.name,
                        "created_on": doc.creation.date().isoformat()
                    })

                    frappe.errprint(f"✅ Cancelled: {doc.name} | Created: {doc.creation.date()}")
        except Exception as e:
            frappe.errprint(f"❌ Failed to cancel {entry.name}: {e}")

    return cancelled_links              
