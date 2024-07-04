import frappe
from urllib.parse import urlencode
import requests

@frappe.whitelist()
def woo_update_normal_item(wooid, item_code):
    woo_settings = frappe.get_doc("Woocommerce API Settings")
    if (woo_settings.url and woo_settings.consumer_key and woo_settings.consumer_secret and woo_settings.price_list):
    
        url = woo_settings.url+"/wp-json/wc/v3/products/"+wooid
        
        consumer_key = woo_settings.consumer_key
        consumer_secret = woo_settings.consumer_secret
        
        up_item_price = []
        item_price = frappe.get_all("Item Price", filters={"item_code":item_code, "price_list": woo_settings.price_list}, fields=["name", "price_list_rate"])
        if item_price:
            for i in item_price:
                up_item_price.append(i.get("price_list_rate"))
        else:
            up_item_price.append(0)
        
        up_bin_qty = []
        bin_doc = frappe.get_all("Bin", filters={"item_code": item_code}, fields=["name", "projected_qty"])
        if bin_doc:
            for j in bin_doc:
                up_bin_qty.append(j.get("projected_qty"))
        else:
            up_bin_qty.append(0)
            
        
        data = {
            "regular_price": str(up_item_price[0]),
            "stock_quantity": sum(up_bin_qty)
        }

        response = requests.put(url, auth=(consumer_key, consumer_secret), json=data)

        if response.status_code == 200:
            frappe.msgprint("Product updated successfully.")
        else:
            frappe.msgprint(f"Failed to update product. Status code: {response.status_code}. Check Woocommerce API Error Log")
            error_doc = frappe.new_doc("Woocommerce API Error Log")
            error_doc.update({
               "item_code": item_code,
               "response_status_code": response.status_code,
               "error_log": response.text
            })
            error_doc.save(ignore_permissions=True)
        
    else:
        frappe.throw("Somthing Missing in Woocommerce API Settings. Please Check")
        
        
        
@frappe.whitelist()
def woo_update_variant_item(wooid, item_code, woovariationid):
    woo_settings = frappe.get_doc("Woocommerce API Settings")
    if (woo_settings.url and woo_settings.consumer_key and woo_settings.consumer_secret and woo_settings.price_list):
    
        url = woo_settings.url+"/wp-json/wc/v3/products/"+wooid+"/variations/"+woovariationid
        
        consumer_key = woo_settings.consumer_key
        consumer_secret = woo_settings.consumer_secret
        
        up_item_price = []
        item_price = frappe.get_all("Item Price", filters={"item_code":item_code, "price_list": woo_settings.price_list}, fields=["name", "price_list_rate"])
        if item_price:
            for i in item_price:
                up_item_price.append(i.get("price_list_rate"))
        else:
            up_item_price.append(0)
        
        up_bin_qty = []
        bin_doc = frappe.get_all("Bin", filters={"item_code": item_code}, fields=["name", "projected_qty"])
        if bin_doc:
            for j in bin_doc:
                up_bin_qty.append(j.get("projected_qty"))
        else:
            up_bin_qty.append(0)
            
        data = {
            "regular_price": str(up_item_price[0]),
            "stock_quantity": sum(up_bin_qty)
        }

        response = requests.put(url, auth=(consumer_key, consumer_secret), json=data)

        if response.status_code == 200:
            frappe.msgprint("Product updated successfully.")
        else:
            frappe.msgprint(f"Failed to update product. Status code: {response.status_code}. Check Woocommerce API Error Log")
            error_doc = frappe.new_doc("Woocommerce API Error Log")
            error_doc.update({
               "item_code": item_code,
               "response_status_code": response.status_code,
               "error_log": response.text
            })
            error_doc.save(ignore_permissions=True)
        
    else:
        frappe.throw("Somthing Missing in Woocommerce API Settings. Please Check")