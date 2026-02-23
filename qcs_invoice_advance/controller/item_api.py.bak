import frappe
import requests

def _get_woocommerce_settings():
    """Get and validate WooCommerce settings."""
    woo_settings = frappe.get_doc("Woocommerce API Settings")
    required_fields = ["url", "consumer_key", "consumer_secret", "price_list"]
    
    if not all(getattr(woo_settings, field) for field in required_fields):
        frappe.throw(
            "Missing required fields in Woocommerce API Settings. "
            "Please check URL, Consumer Key, Consumer Secret, and Price List."
        )
    
    return woo_settings


def _get_item_price(item_code, price_list):
    """Get item price from price list."""
    item_price = frappe.get_all(
        "Item Price",
        filters={"item_code": item_code, "price_list": price_list},
        fields=["price_list_rate"],
        limit=1
    )
    return item_price[0].price_list_rate if item_price else 0


def _get_stock_quantity(item_code):
    """Calculate stock quantity for item (bundle or regular)."""
    # Check if it's a bundle
    bundle_item = frappe.get_all(
        "Product Bundle",
        filters={"name": item_code},
        fields=["name"]
    )
    
    if bundle_item:
        min_stock_ratio = float('inf')
        for bundle in bundle_item:
            bundle_doc = frappe.get_doc("Product Bundle", bundle.name)
            for item in bundle_doc.items:
                try:
                    custom_stock = float(item.custom_in_stock or 0)
                    qty = float(item.qty or 1)
                    if qty > 0:
                        stock_ratio = custom_stock / qty
                        min_stock_ratio = min(min_stock_ratio, stock_ratio)
                except (ValueError, TypeError):
                    continue
        
        return min_stock_ratio if min_stock_ratio != float('inf') else 0
    else:
        # Regular item - get total projected quantity
        bin_result = frappe.db.sql("""
            SELECT COALESCE(SUM(projected_qty), 0) as total_qty
            FROM `tabBin`
            WHERE item_code = %s
        """, item_code, as_dict=True)

        return bin_result[0].total_qty if bin_result else 0


def _update_woocommerce_product(
    wooid, item_code, is_variant=False, variation_id=None
):
    """Core function to update WooCommerce product."""
    woo_settings = _get_woocommerce_settings()
    
    # Build URL
    if is_variant and variation_id:
        base_url = f"{woo_settings.url}/wp-json/wc/v3/products/{wooid}"
        url = f"{base_url}/variations/{variation_id}"
    else:
        url = f"{woo_settings.url}/wp-json/wc/v3/products/{wooid}"
    
    # Get price and stock
    price = _get_item_price(item_code, woo_settings.price_list)
    stock_quantity = _get_stock_quantity(item_code)
    
    data = {
        "regular_price": str(price),
        "stock_quantity": stock_quantity
    }

    try:
        response = requests.put(
            url,
            auth=(woo_settings.consumer_key, woo_settings.consumer_secret),
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            frappe.msgprint("Product updated successfully.")
        else:
            error_msg = (
                f"Failed to update product. "
                f"Status code: {response.status_code}. "
                "Check Woocommerce API Error Log"
            )
            frappe.msgprint(error_msg)
            
            # Log error
            error_doc = frappe.new_doc("Woocommerce API Error Log")
            error_doc.update({
                "item_code": item_code,
                "response_status_code": response.status_code,
                "error_log": response.text
            })
            error_doc.save(ignore_permissions=True)
            
    except requests.RequestException as e:
        frappe.msgprint(f"Request failed: {str(e)}")


@frappe.whitelist()
def woo_update_normal_item(wooid, item_code):
    """Update normal WooCommerce product."""
    return _update_woocommerce_product(wooid, item_code)


@frappe.whitelist()
def woo_update_variant_item(wooid, item_code, woovariationid):
    """Update WooCommerce product variant."""
    return _update_woocommerce_product(wooid, item_code, True, woovariationid)