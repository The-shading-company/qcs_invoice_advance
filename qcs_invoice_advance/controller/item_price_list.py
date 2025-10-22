import frappe
import json
import math

"""
Item Price Update Logic
-----------------------

This script updates Item Prices based on cost and multipliers from the Item Group.

General Rules:
--------------
✅ Never overwrite Item Price to 0 — if no valid cost is available, keep existing price as-is.
✅ `custom_avoid_auto_update_price_list_based_on_item_group = 1` → Always skip.
✅ Templates (`has_variants = 1`) → Always skip.

Standard Items (not bundles):
-----------------------------
- If flagged → skip.
- If no cost (`custom_average_cost` and `valuation_rate` ≤ 0) → skip.
- If cost > 0 → use cost × multiplier → update/create Item Price.

Bundles (Product Bundle):
-------------------------
- Cron job → always skip bundles.
- Button on Item Group → can update bundles if:
    - Not flagged.
    - `Product Bundle.custom_item_total_cost > 0`.
    - Uses bundle total cost × multiplier → update/create Item Price.
- If bundle total cost ≤ 0 → skip.

Button vs. Cron:
----------------
- Cron → runs daily → standard items only, skips bundles.
- Button → manual → updates both standard items and bundles (if not flagged).

Multipliers:
------------
- Contract, Dealer, and Retail multipliers are retrieved from the Item Group.
- Applies only if multiplier > 0 and cost > 0.

Summary Table:
--------------
| Item Type       | Flag = 1 (avoid) | Flag = 0 + No Cost | Flag = 0 + Has Cost |
|-----------------|------------------|---------------------|---------------------|
| Standard Item   | 🚫 Skip          | 🚫 Skip             | ✅ Update           |
| Bundle (cron)   | 🚫 Skip          | 🚫 Skip             | 🚫 Skip            |
| Bundle (button) | 🚫 Skip          | 🚫 Skip             | ✅ Update if bundle total cost > 0 |
"""

import math
import frappe

def compute_price(item, multiplier, use_bundle_cost=False):
    """
    Compute the price for an item using:
    - bundle total cost (if use_bundle_cost & bundle & >0), else
    - custom_average_cost (if >0), else
    - valuation_rate (if >0)
    Then multiply by multiplier.
    Result is rounded up to nearest 10.
    """
    cost = 0

    # If instructed & is a bundle → fetch bundle cost
    if use_bundle_cost and frappe.db.exists("Product Bundle", {"new_item_code": item.name}):
        bundle = frappe.get_doc("Product Bundle", {"new_item_code": item.name})
        if bundle.custom_item_total_cost and bundle.custom_item_total_cost > 0:
            cost = float(bundle.custom_item_total_cost)

    # fallback if no bundle cost
    if cost <= 0:
        if item.custom_average_cost and float(item.custom_average_cost) > 0:
            cost = float(item.custom_average_cost)
        elif item.valuation_rate and float(item.valuation_rate) > 0:
            cost = float(item.valuation_rate)

    price = cost * multiplier if cost > 0 and multiplier > 0 else 0

    # round up to nearest 10
    if price > 0:
        price = math.ceil(price / 10) * 10

    return price


def update_or_create_item_price(item_code, price_list, rate):
    """
    Update existing Item Price if found, or create one.
    If multiple exist for the same item & price_list, keeps one & removes others.
    """
    prices = frappe.get_all(
        "Item Price",
        filters={"item_code": item_code, "price_list": price_list},
        fields=["name"]
    )

    if prices:
        # update the first one
        frappe.db.set_value("Item Price", prices[0].name, "price_list_rate", rate)
        frappe.logger().info(f"[Item Price] Updated {item_code} - {price_list}: {rate}")

        # delete any duplicates
        for extra in prices[1:]:
            frappe.delete_doc("Item Price", extra.name, ignore_permissions=True)
            frappe.logger().info(f"[Item Price] Deleted duplicate {extra.name} for {item_code} - {price_list}")

    else:
        # no existing → create new
        doc = frappe.new_doc("Item Price")
        doc.update({
            "item_code": item_code,
            "price_list": price_list,
            "price_list_rate": rate
        })
        doc.save(ignore_permissions=True)
        frappe.logger().info(f"[Item Price] Created {item_code} - {price_list}: {rate}")


def process_item(item, price_data, skip_bundles=True):
    """
    Process a single item for all given price lists.
    If skip_bundles=True → bundles are ignored (cron).
    If skip_bundles=False → bundles allowed & bundle cost is fetched.
    Skips item if flag is set.

    NEW: If an Item has a BOM, skip it entirely here because BOM-managed pricing
    is calculated elsewhere.
    """
    # Skip templates
    if item.has_variants:
        frappe.logger().info(f"Skipping template: {item.name}")
        return

    # If this item has a BOM, skip — BOM pricing is handled elsewhere
    if frappe.db.exists("BOM", {"item": item.name}):
        frappe.logger().info(f"Skipping {item.name} — BOM exists; price managed by BOM process.")
        return

    # Skip if flagged
    if item.custom_avoid_auto_update_price_list_based_on_item_group:
        frappe.logger().info(f"Skipping {item.name} — flagged to avoid auto update.")
        return

    # skip bundles for cron
    if skip_bundles and frappe.db.exists("Product Bundle", {"new_item_code": item.name}):
        frappe.logger().info(f"Skipping bundle: {item.name} (cron)")
        return

    is_bundle = frappe.db.exists("Product Bundle", {"new_item_code": item.name})

    for label, multiplier, price_list in price_data:
        if not price_list or not multiplier or multiplier <= 0:
            frappe.logger().info(f"[Item Price] Skipping {label} for {item.name} — invalid multiplier or price list.")
            continue

        rate = compute_price(item, multiplier, use_bundle_cost=not skip_bundles and is_bundle)
        if rate <= 0:
            frappe.logger().info(f"[Item Price] Skipping {label} for {item.name} — computed rate is 0.")
            continue

        update_or_create_item_price(item.name, price_list, rate)
        frappe.logger().info(f"[Item Price] Updated {item.name} → {label}: {rate}")


@frappe.whitelist()
def update_item_price(item_group, contract_price, dealer_price, retail_price,
                      retail_price_list, contract_price_list, dealer_price_list):
    """
    Button: Update all items in a single item group for all 3 price lists.
    Includes bundles.
    """
    contract_price = float(json.loads(contract_price))
    dealer_price = float(json.loads(dealer_price))
    retail_price = float(json.loads(retail_price))

    items = frappe.get_all(
        "Item",
        filters={"item_group": item_group},
        fields=["name"]
    )

    if not items:
        frappe.msgprint("No items found in the Item Group.")
        return

    price_data = [
        ("Contract", contract_price, contract_price_list),
        ("Dealer", dealer_price, dealer_price_list),
        ("Retail", retail_price, retail_price_list),
    ]

    for i in items:
        item = frappe.get_doc("Item", i.name)
        process_item(item, price_data, skip_bundles=False)  # Button can update bundles

    frappe.msgprint("Item Price List Updated.")


@frappe.whitelist()
def item_price_list(item_code, price_list):
    """
    API: Return computed price for a single item & given price list.
    """
    item = frappe.get_doc("Item", item_code)

    if item.custom_avoid_auto_update_price_list_based_on_item_group:
        return 0

    item_group = frappe.get_doc("Item Group", item.item_group)

    mapping = {
        item_group.custom_contract_price_list: item_group.custom_contract_price,
        item_group.custom_dealer_price_list: item_group.custom_dealer_price,
        item_group.custom_retail_price_list: item_group.custom_retail_price,
    }

    multiplier = mapping.get(price_list)
    if multiplier:
        return compute_price(item, multiplier)

    return 0


@frappe.whitelist()
def cron_update_item_price():
    """
    Cron: updates all item groups and their items.
    Skips bundles, templates, flagged items & items with no cost.
    """
    all_groups = frappe.get_all("Item Group", fields=["name"])

    for g in all_groups:
        group = frappe.get_doc("Item Group", g.name)

        price_data = [
            ("Contract", group.custom_contract_price, group.custom_contract_price_list),
            ("Dealer", group.custom_dealer_price, group.custom_dealer_price_list),
            ("Retail", group.custom_retail_price, group.custom_retail_price_list),
        ]

        items = frappe.get_all(
            "Item",
            filters={
                "item_group": group.name
            },
            fields=["name"]
        )

        if not items:
            continue

        for i in items:
            item = frappe.get_doc("Item", i.name)
            process_item(item, price_data, skip_bundles=True)  # Cron skips bundles

    frappe.logger().info("[Item Price] Daily cron completed.")

