import frappe
import re
from typing import Dict, Any

def _calculate_item_cost(row) -> float:
    """Helper function to calculate item cost with proper error handling."""
    item_cost = row.custom_item_cost or 0
    if isinstance(item_cost, str):
        try:
            item_cost = float(item_cost)
        except ValueError:
            # Extract first valid float from concatenated string
            match = re.search(r'\d+\.?\d*', item_cost)
            item_cost = float(match.group()) if match else 0
    return float(item_cost)


def _update_bundle_item(row, item_doc: Dict[str, Any]) -> None:
    """Update a single bundle item with cost and stock information."""
    row.custom_average_rate = float(item_doc.custom_average_cost or 0)
    row.custom_item_validation_rate = float(item_doc.valuation_rate or 0)
    row.custom_in_stock = get_item_stock(item_doc.name)

    # Decide which cost to use
    if row.custom_average_rate > 0:
        row.custom_item_cost = row.custom_average_rate
    else:
        row.custom_item_cost = row.custom_item_validation_rate

    row.custom_item_total_cost = (row.qty or 0) * row.custom_item_cost


def cron_update_product_bundle() -> None:
    """Cron: updates all Product Bundles with total component costs."""
    bundles = frappe.get_all("Product Bundle", filters={"disabled": 0},
                           fields=["name"])

    for bundle_info in bundles:
        try:
            doc = frappe.get_doc("Product Bundle", bundle_info.name)
            total_cost = 0

            for row in doc.items:
                # Only fetch needed fields instead of full document
                item_doc = frappe.db.get_value(
                    "Item", row.item_code,
                    ["name", "custom_average_cost", "valuation_rate"],
                    as_dict=True
                )

                if not item_doc:
                    frappe.logger().warning(
                        f"Item {row.item_code} not found for bundle {doc.name}"
                    )
                    continue

                _update_bundle_item(row, item_doc)
                total_cost += row.custom_item_total_cost
            
            doc.custom_item_total_cost = total_cost

            # Update retail price and margin
            _update_retail_price_info(doc)
            
            doc.save(ignore_permissions=True)
            
            frappe.logger().info(
                f"[Bundle] Updated: {doc.name} — total cost: {total_cost}, "
                f"retail: {getattr(doc, 'custom_retail_price_list', None)}, "
                f"margin: {getattr(doc, 'custom_retail_margin', None)}"
            )
            
        except Exception as e:
            frappe.logger().error(
                f"Error updating bundle {bundle_info.name}: {str(e)}"
            )
            continue


def _update_retail_price_info(doc) -> None:
    """Update retail price and margin information for the bundle."""
    if not getattr(doc, "new_item_code", None):
        return

    retail_price = frappe.db.get_value(
        "Item Price",
        {"price_list": "Retail", "item_code": doc.new_item_code},
        "price_list_rate",
    )
    
    if retail_price:
        cost = float(doc.custom_item_total_cost or 0)
        margin = ((float(retail_price) - cost) / cost * 100) if cost > 0 else 0
        doc.custom_retail_price_list = float(retail_price)
        doc.custom_retail_margin = round(margin, 2)


def get_item_stock(item_code):
    """
    Returns total stock quantity of an item.
    """
    qty = frappe.db.sql("""
        SELECT COALESCE(SUM(actual_qty), 0)
        FROM `tabBin`
        WHERE item_code = %s
    """, (item_code,))[0][0]

    return qty


@frappe.whitelist()
def get_valuation(item_code):
    """
    Get latest valuation rate of an item.
    """
    rate = frappe.db.sql("""
        SELECT valuation_rate
        FROM `tabStock Ledger Entry`
        WHERE item_code = %s
        ORDER BY posting_date DESC, posting_time DESC
        LIMIT 1
    """, (item_code,))

    rate = rate[0][0] if rate else None

    if not rate:
        rate = frappe.db.get_value("Item", item_code, "valuation_rate")

    return rate or 0


def cal_cost(self, event) -> None:
    """Hook: calculate and set total cost of components in a document."""
    if not self.items:
        return

    total_cost = 0
    for row in self.items:
        # Refresh item data when item_code changes
        if hasattr(row, 'item_code') and row.item_code:
            _refresh_bundle_item_data(row)

        item_cost = _calculate_item_cost(row)
        row.custom_item_total_cost = float((row.qty or 0) * item_cost)
        total_cost += row.custom_item_total_cost

    self.custom_item_total_cost = total_cost


def _refresh_bundle_item_data(row) -> None:
    """Refresh bundle item data when item_code changes."""
    try:
        # Get fresh item data
        item_doc = frappe.db.get_value(
            "Item", row.item_code,
            ["name", "custom_average_cost", "valuation_rate"],
            as_dict=True
        )

        if item_doc:
            row.custom_average_rate = float(
                item_doc.custom_average_cost or 0
            )
            row.custom_item_validation_rate = float(
                item_doc.valuation_rate or 0
            )
            row.custom_in_stock = get_item_stock(item_doc.name)

            # Update the cost based on new item data
            if row.custom_average_rate > 0:
                row.custom_item_cost = row.custom_average_rate
            else:
                row.custom_item_cost = row.custom_item_validation_rate

    except Exception as e:
        frappe.logger().error(
            f"Error refreshing item data for {row.item_code}: {str(e)}"
        )


@frappe.whitelist()
def bundle_item_stock(item_code):
    up_bin_qty = []
    bin_doc = frappe.get_all("Bin", filters={"item_code": item_code}, fields=["name", "actual_qty"])
    if bin_doc:
        for j in bin_doc:
            up_bin_qty.append(j.get("actual_qty"))
    else:
        up_bin_qty.append(0)

    qty = sum(up_bin_qty)
    return qty
