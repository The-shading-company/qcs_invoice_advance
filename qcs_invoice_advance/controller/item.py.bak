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

#This creates a bom for awf variants
def create_bom_for_awf_item(doc, method=None):
    """
    Auto-create a BOM for AWF-* items after Item insert.
    Parses item_code for canopy/fabric/flap details, fetches minutes/qty from TSC Stitching Cost,
    creates BOM; submits if minutes > 0 and a matching row was found, else leaves as Draft.
    """
    item_code = (doc.item_code or "").strip()
    if not item_code.startswith("AWF"):
        return

    # Avoid duplicate default BOMs
    existing_bom = frappe.db.get_value(
        "BOM",
        {"item": doc.name, "is_active": 1, "is_default": 1, "docstatus": ["!=", 2]},
        "name",
    )
    if existing_bom:
        return

    # -------- Parse item code --------
    parts = item_code.split("-")
    if len(parts) < 5:
        frappe.log_error(f"AWF parse failed (too few parts): {item_code}", "AWF BOM")
        return

    canopy_type = parts[1]          # e.g., UMB or AWN
    canopy_size = parts[2]          # e.g., 3x3 (or diameter token)
    fabric_code_token = parts[3]    # start of fabric code

    flap_size = None
    flap_type = None

    # Fabric code can be like "R-196" or "2124-03"
    # If parts[4] contains 'cm', it's a flap size, otherwise it's part of the fabric code suffix.
    if len(parts) > 4 and "cm" in parts[4]:
        fabric_code = fabric_code_token
        flap_size = parts[4]
        flap_type = parts[5] if len(parts) > 5 else None
    else:
        # combine fabric code token + next token
        fabric_code = f"{fabric_code_token}-{parts[4]}" if len(parts) > 4 else fabric_code_token
        flap_size = parts[5] if len(parts) > 5 else None
        flap_type = parts[6] if len(parts) > 6 else None

    # Verify fabric item exists
    if not frappe.db.exists("Item", fabric_code):
        frappe.log_error(f"Fabric item not found: {fabric_code} (from {item_code})", "AWF BOM")
        return

    # -------- Fetch stitching data --------
    stitch_minutes = None
    fabric_qty = None
    stitching_found = False

    try:
        sc = frappe.get_doc("TSC Stitching Cost", "TSCS-0020")
        for row in sc.get("cost_table_tab", []):
            if row.canopy_type == canopy_type and row.canopy_size == canopy_size:
                fabric_qty = flt(row.custom_flap_fab_qty)
                if (flap_type or "").upper() == "STR":
                    stitch_minutes = flt(row.custom_flap_str_min)
                elif (flap_type or "").upper() in {"SCAL", "SCALL", "SCALLOP", "SCALLOPED"}:
                    # tolerate variants of 'SCALL'
                    stitch_minutes = flt(row.custom_flap_sca_min)
                else:
                    # unknown flap type → fall back to 0 minutes
                    stitch_minutes = 0.0
                stitching_found = True
                break
    except Exception:
        frappe.log_error(frappe.get_traceback(), "AWF BOM: Stitching Cost Fetch Error")

    # Defaults if not found
    if fabric_qty is None:
        fabric_qty = 1.0
    if stitch_minutes is None:
        stitch_minutes = 0.0

    # Optional: ensure routing exists before assigning
    routing_name = "stitching" if frappe.db.exists("Routing", "stitching") else None

    # -------- Create BOM --------
    try:
        bom_dict = {
            "doctype": "BOM",
            "item": doc.name,
            "is_active": 1,
            "is_default": 1,
            "allow_alternative_item": 1,
            "set_rate_of_sub_assembly_item_based_on_bom": 0,
            "with_operations": 1,
            # If you use meters for fabric, set uom to "Meter" and qty accordingly
            "items": [{
                "item_code": fabric_code,
                "qty": fabric_qty,
                "uom": "Nos",   # change to "Meter" if that’s your store unit for fabric
            }],
            "operations": [{
                "operation": "Stitching",
                "workstation": "Stitching Station",
                "workstation_type": "Stitching",
                "time_in_mins": stitch_minutes,
            }],
        }
        if routing_name:
            bom_dict["routing"] = routing_name

        bom = frappe.get_doc(bom_dict)
        bom.insert(ignore_permissions=True)

        # Submit only when we have a matched row and minutes > 0
        if stitching_found and stitch_minutes > 0:
            bom.submit()
            frappe.log_error(f"Submitted BOM {bom.name} for {item_code} (fabric {fabric_code}, flap {flap_size}/{flap_type})", "AWF BOM")
        else:
            frappe.log_error(f"Draft BOM {bom.name} for {item_code} (awaiting approval / minutes={stitch_minutes})", "AWF BOM")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "AWF BOM Creation Error")


#this creates a bom for rep variants
def create_bom_for_rep_variant(doc, method=None):
    """Auto-create & submit a BOM for REP-* items right after Item insert."""
    try:
        item_code = (doc.item_code or "").strip()
        if not item_code.startswith("REP-"):
            return

        # Skip if a default, submitted BOM already exists
        existing_bom = frappe.db.get_value(
            "BOM",
            {"item": doc.name, "is_active": 1, "is_default": 1, "docstatus": 1},
            "name",
        )
        if existing_bom:
            return

        parts = item_code.split("-")
        # Valid formats:
        #  - REP-<FabricCode>-<Meters>-<Minutes>        (len=4)
        #  - REP-<FabricPrefix>-<FabricCode>-<M>-<Min>  (len=5)
        if not (4 <= len(parts) <= 5):
            frappe.log_error(f"Invalid REP code format: {item_code}", "REP BOM")
            return

        fabric_code = f"{parts[1]}-{parts[2]}" if len(parts) == 5 else parts[1]

        try:
            meters = flt(parts[-2])
            minutes = flt(parts[-1])
        except Exception:
            frappe.log_error(f"Non-numeric meters/minutes in: {item_code}", "REP BOM")
            return

        if meters <= 0 or minutes <= 0:
            frappe.log_error(f"Meters/Minutes must be > 0: {item_code}", "REP BOM")
            return

        # Ensure fabric item exists
        if not frappe.db.exists("Item", fabric_code):
            frappe.log_error(f"Fabric item not found: {fabric_code} (from {item_code})", "REP BOM")
            return

        # Optional routing if present
        routing_name = "stitching" if frappe.db.exists("Routing", "stitching") else None

        bom_dict = {
            "doctype": "BOM",
            "item": doc.name,
            "is_active": 1,
            "is_default": 1,
            "quantity": 1,
            "with_operations": 1,
            "items": [{"item_code": fabric_code, "qty": meters}],
            "operations": [{
                "operation": "Stitching",
                "workstation": "Stitching Station",
                "workstation_type": "Stitching",
                "time_in_mins": minutes
            }],
        }
        if routing_name:
            bom_dict["routing"] = routing_name

        bom = frappe.get_doc(bom_dict)
        bom.insert(ignore_permissions=True)
        bom.submit()

        # Quiet audit log
        frappe.log_error(f"Created BOM {bom.name} for {item_code}", "REP BOM")

    except Exception:
        frappe.log_error(frappe.get_traceback(), "REP BOM Creation Error")

#this creates a canopy on item creation for Canopies Awn Bli and Umbrellas . Uses parsing rather than getting from item attributes
def create_canopy_bom(self, event):
	if not self.item_code.startswith("CAN-"):
		return

	try:
		parts = self.item_code.split("-")
		if len(parts) < 5:
			frappe.log_error(f"Invalid item code format: {self.item_code}", "BOM Creation Skipped")
			return

		canopy_type = parts[1]  # AWN / BLI / UMB
		canopy_size = parts[2]  # e.g., 6x3
		fabric_code = "-".join(parts[4:]).strip()

		if not fabric_code or fabric_code == self.item_code:
			frappe.log_error(f"Fabric code parsing failed for {self.item_code}. Got: '{fabric_code}'", "BOM Creation Skipped")
			return

		if not frappe.db.exists("Item", fabric_code):
			frappe.log_error(f"Fabric item '{fabric_code}' not found for {self.item_code}", "BOM Creation Skipped")
			return

		stitching_found = False
		stitching_docs = frappe.get_all("TSC Stitching Cost", pluck="name")

		for docname in stitching_docs:
			s_doc = frappe.get_doc("TSC Stitching Cost", docname)
			for row in s_doc.cost_table_tab:
				if row.get("canopy_type") == canopy_type and row.get("canopy_size") == canopy_size:
					fabric_qty = float(row.get("canopy_qty") or 1)
					stitch_minutes = int(row.get("custom_tsc_stitching_minutes") or 0)
					op_cost = float(row.get("no_flap_stitching_cost") or 0)

					existing = frappe.get_all("BOM", filters={"item": self.name}, limit=1)
					if existing:
						bom_doc = frappe.get_doc("BOM", existing[0].name)
						if bom_doc.docstatus == 0:
							bom_doc.items[0].qty = fabric_qty
							bom_doc.fg_based_operating_cost = 1
							bom_doc.operating_cost_per_bom_quantity = op_cost
							bom_doc.save(ignore_permissions=True)
							bom_doc.submit()
							frappe.logger().info(f"BOM updated for {self.name}")
					else:
						doc = frappe.new_doc("BOM")
						doc.update({
							"item": self.name,
							"is_active": 1,
							"is_default": 1,
							"with_operations": 1,
							"routing": "stitching",
							"items": [
								{"item_code": fabric_code, "qty": fabric_qty}
							],
							"operations": [
								{
									"operation": "Stitching",
									"workstation": "Stitching Station",
									"workstation_type": "Stitching",
									"time_in_mins": stitch_minutes
								}
							],
							"fg_based_operating_cost": 1,
							"operating_cost_per_bom_quantity": op_cost
						})
						doc.insert(ignore_permissions=True)
						doc.submit()
						frappe.logger().info(f"BOM created for {self.name}")
					
					stitching_found = True
					break
			if stitching_found:
				break

		if not stitching_found:
			frappe.logger().warning(f"No stitching row found for {self.name} (Type: {canopy_type}, Size: {canopy_size})")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"BOM Auto-Creation Error for {self.name}")
 

#moving to seperate code

# def create_shade_sail_price(self, event):
# 	sh_type = ""
# 	sw = 0
# 	sl = 0
# 	sp = 0
# 	sc = 0
# 	sb = 0
# 	if self.variant_of == "SHA-T":
# 		for i in self.attributes:
# 			if i.attribute == "Shade Shape":
# 				sh_type = i.attribute_value
# 			if i.attribute == "Shade Width":
# 				sw = flt(i.attribute_value)
# 			if i.attribute == "Shade Length":
# 				sl = flt(i.attribute_value)
# 			if i.attribute == "Posts":
# 				sp = flt(i.attribute_value)
# 			if i.attribute == "Concrete":
# 				sc = flt(i.attribute_value)
# 			if i.attribute == "Wall Bracket":
# 				sb = flt(i.attribute_value)
# 	if sh_type == "Square":
# 		f_width = math.ceil(flt(sw) / 3)
# 		f_qty = f_width * flt(sl)
# 		f_cost = 25 * f_qty
# 		s_size = (f_width * 2) + (flt(sl) * 2)
# 		cable_cost = s_size * 6
# 		bracket_cost = flt(sb) * 22 * 2
# 		post_cost = flt(sp) * 380 * 2
# 		post_pc_cost = flt(sp) * 245 * 2
# 		post_braket_cost = flt(sp) * bracket_cost * 2
# 		dshackle_cost = flt(sp) * 5 * 2
# 		wire_clamp_cost = 2 * 2 * 2
# 		eyelet_cost = flt(sp) * 18 * 2
# 		post_cap_cost = flt(sp) * 21 * 2
# 		stitching_cost = flt(sw) * flt(sl) * 12.5 * 2.1
# 		installation_cost = 230 * 1.65
# 		concrete_cost = flt(sc) * 607 * 1.75
# 		total_price = f_cost + cable_cost + bracket_cost + post_cost + post_pc_cost + post_braket_cost + dshackle_cost + wire_clamp_cost + eyelet_cost + post_cap_cost + stitching_cost + installation_cost + concrete_cost
# 		if total_price > 0:
# 			frappe.msgprint("Retail Price List Added")
# 		if not frappe.db.exists('Item Price', {"item_code": self.name, "price_list": "Retail"}):
# 			ip_doc = frappe.new_doc("Item Price")
# 			ip_doc.item_code = self.name
# 			ip_doc.price_list = "Retail"
# 			ip_doc.price_list_rate = total_price
# 			ip_doc.save(ignore_permissions=True)


			

#updates the canopy bom for changes. 
def update_canopy_bom(self, event):
	if not self.item_code.startswith("CAN-"):
		return

	try:
		parts = self.item_code.split("-")
		if len(parts) < 5:
			frappe.log_error(f"Invalid item code format: {self.item_code}", "Canopy BOM Update Skipped")
			return

		canopy_type = parts[1]  # e.g., 'AWN', 'BLI', 'UMB'
		canopy_size = parts[2]  # e.g., '4x3'
		fabric_code = "-".join(parts[4:]).strip()

		if not fabric_code or fabric_code == self.item_code:
			frappe.log_error(f"Fabric code parsing failed for {self.item_code}. Got: '{fabric_code}'", "Canopy BOM Update Skipped")
			return

		stitching_docs = frappe.get_all("TSC Stitching Cost", pluck="name")

		for docname in stitching_docs:
			s_doc = frappe.get_doc("TSC Stitching Cost", docname)
			for row in s_doc.cost_table_tab:
				if row.get("canopy_type") == canopy_type and row.get("canopy_size") == canopy_size:
					fabric_qty = float(row.get("canopy_qty") or 1)
					stitch_minutes = int(row.get("custom_tsc_stitching_minutes") or 0)
					op_cost = float(row.get("no_flap_stitching_cost") or 0)

					boms = frappe.get_all("BOM", filters={"item": self.name, "docstatus": 0})
					for b in boms:
						bom_doc = frappe.get_doc("BOM", b.name)

						# Update fabric quantity
						if bom_doc.items:
							bom_doc.items[0].qty = fabric_qty

						# Update stitching time
						if bom_doc.operations:
							bom_doc.operations[0].time_in_mins = stitch_minutes

						bom_doc.fg_based_operating_cost = 1
						bom_doc.operating_cost_per_bom_quantity = op_cost
						bom_doc.save(ignore_permissions=True)
						frappe.logger().info(f"Canopy BOM updated for {self.name}")

					return  # Stop after first match

		frappe.logger().warning(f"No stitching row found for {self.name} (Type: {canopy_type}, Size: {canopy_size})")

	except Exception as e:
		frappe.log_error(frappe.get_traceback(), f"Canopy BOM Update Error for {self.name}")
							
def delete_bom(self, event):
	
	if (frappe.get_all("BOM", filters={"item": self.name})):
		bom = frappe.get_all("BOM", filters={"item": self.name})
		for k in bom:
			bom_doc = frappe.get_doc("BOM", k)
			if (bom_doc.docstatus == 0 or bom_doc.docstatus == 2):
				frappe.delete_doc("BOM", bom_doc.name, ignore_permissions=True)
			if (bom_doc.docstatus == 1):
				bom_doc.cancel()
				frappe.delete_doc("BOM", bom_doc.name, ignore_permissions=True)


#updated version to fix not adding images. Also now handles static images for other items

def add_image(self, event):
    try:
        # ✅ Prefixes that use fabric attribute logic
        dynamic_prefixes = ["CAN", "REP", "AWF"]

        # ✅ Static prefix-to-image path map (for other items)
        static_image_map = {
            "PER-SRA": "/private/files/Sierra-Bioclimatic-Pergola-UAE-1024x5414edd111f1570.jpg",
            "PER-LWA": "/files/Liwa Pergola.jpg",
            "UMB-PALN": "/files/Palazzo%20Noblesse%20600x600%20M4%20Base.jpg",
            "AWN-KUAD": "/files/Kuadbox%20Awning%20Anthracite91615c.jpg",
            "AWN-STOS3": "/files/StorboxS300040180.jpg",
			"AWN-MOD": "/files/Modulbox.jpg",
            "SHA-T": "/files/Shade%20Sail%20Tensioned0b263a4121b25b9981660810.jpg"
        }

        # ───────────────────────────────────────────────
        # ✅ CASE 1: Dynamic image based on Fabric Color
        # ───────────────────────────────────────────────
        if self.variant_of and any(self.variant_of.startswith(prefix) for prefix in dynamic_prefixes):
            fabric_color = None
            for attr in self.attributes:
                if attr.attribute == "Fabric Color":
                    fabric_color = attr.attribute_value
                    break

            if not fabric_color:
                return

            custom_item_code = frappe.db.get_value(
                "Item Attribute Value",
                {"attribute_value": fabric_color},
                "custom_item_code"
            )

            if not custom_item_code:
                return

            image_url = frappe.db.get_value("Item", custom_item_code, "image")
            if not image_url:
                return

            if image_url.startswith("http"):
                frappe.db.set_value("Item", self.name, "image", image_url)
                return

            file_path = frappe.get_site_path("public", image_url.lstrip("/"))
            if os.path.exists(file_path):
                frappe.db.set_value("Item", self.name, "image", image_url)
                return

        # ───────────────────────────────────────────────
        # ✅ CASE 2: Static fallback for other prefixes
        # ───────────────────────────────────────────────
        for prefix, image_path in static_image_map.items():
            if self.name.startswith(prefix):
                frappe.db.set_value("Item", self.name, "image", image_path)
                return

    except Exception:
        pass  # Silent fail in production

#checks if image exists and adds it to the item
# def add_image(self, event):
#     if self.variant_of == "CAN":
#         for item in self.attributes:
#             if item.attribute == "Fabric Color":
#                 att_list = frappe.get_all("Item Attribute Value", filters={"attribute_value": item.attribute_value})
#                 if att_list:
#                     att_raw = frappe.db.get_value("Item Attribute Value", {"attribute_value": item.attribute_value}, "custom_item_code")
#                     image_url = frappe.get_value("Item", att_raw, "image")
#                     if not image_url:
#                         continue

#                     org_l = frappe.get_all("File", filters={"file_url": image_url})
#                     if not org_l:
#                         continue

#                     org_f = frappe.get_doc("File", org_l[0].name)

#                     # check if the file actually exists
#                     file_path = frappe.get_site_path("public", org_f.file_url.lstrip("/"))
#                     if not os.path.exists(file_path):
#                         frappe.logger().warning(f"File missing on disk: {file_path}. Skipping attachment.")
#                         continue

#                     fm = frappe.new_doc("File")
#                     fm.file_name = org_f.file_name
#                     fm.file_type = org_f.file_type
#                     fm.file_url = org_f.file_url
#                     fm.attached_to_doctype = "Item"
#                     fm.attached_to_name = self.name
#                     fm.attached_to_field = "image"
#                     fm.save()
					


#render jinja template in item desc
# added frame color and fabric color
def set_dynamic_item_description(doc, method):
	if doc.custom_jinja_desc:
		# Prepare your context for the Jinja template. This might include other fields or data as needed.
			context = {
				'doc': doc, 'variants': doc.variants if hasattr(doc, 'variants') else []
				# Include any additional variables or tables you need in your Jinja template.
				# E.g., 'variants': doc.variants if hasattr(doc, 'variants') else []
			}
			
			# Render the description using the custom Jinja template and the context
			rendered_description = render_template(doc.custom_jinja_desc, context)
			
			# Set the rendered description to the item's description field
			doc.description = rendered_description

	if doc.variant_of:
		c_size = ""
		c_color = ""
		for v in doc.attributes:
			if v.attribute == "Fabric Color":
				c_color = v.attribute_value
			if v.attribute == "Frame Color":
				c_color = v.attribute_value
			if v.attribute == "Size":
				c_size = v.attribute_value
				if 'x' in c_size:
					part1, part2 = c_size.split('x')
					value1 = int(float(part1) * 100)
					value2 = int(float(part2) * 100)
					doc.custom_tsc_size = str(value1) + " x " + str(value2)
				else:
					doc.custom_tsc_size = c_size
		if not doc.custom_tsc_color:
			doc.custom_tsc_color = c_color

#this adds the selling price for items created in the bom. only active and default BOMs get their price updated
# this runs from a event hook from submit and update after submit
def add_sale_price(self, event):
	if not (self.is_active and self.is_default):
		# Skip if BOM is not active or not default
		return

	multipliers = {
		"Retail": 2.30,
		"Contract": 1.95,
		"Dealer": 1.85
	}

	for price_list, multiplier in multipliers.items():
		item_prices = frappe.get_all("Item Price", filters={"item_code": self.item, "price_list": price_list})

		new_price = round(self.total_cost * multiplier)

		if item_prices:
			for i in item_prices:
				ip_doc = frappe.get_doc("Item Price", i)
				ip_doc.price_list_rate = new_price
				ip_doc.save(ignore_permissions=True)
		else:
			ip_doc = frappe.new_doc("Item Price")
			ip_doc.item_code = self.item
			ip_doc.price_list = price_list
			ip_doc.price_list_rate = new_price
			ip_doc.save(ignore_permissions=True)


def tsc_custom_accounts(self, event):
	if self.doctype == "Sales Invoice":
		for item in self.items:
			cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Expense" })
			if len(cogs) > 0:
				item.expense_account = cogs[0].name
			rev = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Income" })
			if len(rev) > 0:
				item.income_account = rev[0].name

	if self.doctype == "Delivery Note":
		for item in self.items:
			cogs = frappe.get_all("Account", filters={"custom_customer_type":frappe.get_value("Customer", self.customer, "customer_type"), "custom_item_group":item.item_group, "root_type":"Expense" })
			if len(cogs) > 0:
				item.expense_account = cogs[0].name

# #This script adds margins for quotation. Iterates through the line items and updated either from bom or from item cost.
# def add_margins(self, event):
# 	total_cost = 0
# 	total_cost_with_qty = 0
# 	total_margin = 0
# 	total_margin_with_qty = 0

# 	for item in self.items:
# 		item_cost = 0

# 		# ── Try BOM first ──
# 		bom = frappe.get_all("BOM", filters={"item": item.item_code, "is_active": 1, "is_default": 1})
# 		if bom:
# 			bom_doc = frappe.get_doc("BOM", bom[0].name)
# 			item_cost = bom_doc.total_cost
# 		else:
# 			# ── Fallback to Item Master: custom_average_cost → valuation_rate ──
# 			try:
# 				item_doc = frappe.get_doc("Item", item.item_code)
# 				if item_doc.custom_average_cost:
# 					item_cost = float(item_doc.custom_average_cost)
# 				else:
# 					item_cost = float(item_doc.valuation_rate or 0)
# 			except Exception as e:
# 				frappe.log_error(f"Error fetching cost for item {item.item_code}: {e}", "Add Margins Error")
# 				item_cost = 0

# 		# ── Assign cost ──
# 		try:
# 			qty = float(item.qty or 0)
# 			item.custom_tsc_cost = item_cost
# 			item.custom_tsc_cost_with_qty = item_cost * qty
# 			total_cost += item_cost
# 			total_cost_with_qty += item.custom_tsc_cost_with_qty
# 		except Exception as e:
# 			frappe.log_error(f"Error calculating cost_with_qty for {item.item_code}: {e}", "Add Margins Error")
# 			item.custom_tsc_cost = 0
# 			item.custom_tsc_cost_with_qty = 0

# 		# ── Margin calculations ──
# 		if item_cost > 0:
# 			try:
# 				item.custom_tsc_margin = float(item.rate) - item_cost
# 				with_qty_margin = (float(item.rate) * qty) - (item_cost * qty)
# 				total_margin += item.custom_tsc_margin
# 				total_margin_with_qty += with_qty_margin

# 				if item.custom_tsc_margin > 0:
# 					item.custom_tsc_margin_per = (item.custom_tsc_margin * 100) / item_cost
# 			except Exception as e:
# 				frappe.log_error(f"Error calculating margin for {item.item_code}: {e}", "Add Margins Error")

# 	# ── Final totals ──
# 	self.custom_total_cost = total_cost_with_qty
# 	if self.custom_total_cost > 0:
# 		try:
# 			self.custom_total_margin = self.net_total - total_cost_with_qty
# 			self.custom_margin_percent = (self.custom_total_margin * 100) / self.custom_total_cost
# 		except Exception as e:
# 			frappe.log_error(f"Error calculating document margin: {e}", "Add Margins Error")

# @frappe.whitelist()
# def recalculate_sales_order_margins(sales_order):
#     doc = frappe.get_doc("Sales Order", sales_order)
#     from qcs_invoice_advance.controller.item import add_margins_sales_order
#     add_margins_sales_order(doc, None)
#     doc.save(ignore_permissions=True)

# #this adds margin to sales orders just like the script above for quotations.
# def add_margins_sales_order(doc, event):
#     total_cost = 0
#     total_cost_with_qty = 0
#     total_margin = 0
#     total_margin_with_qty = 0

#     for item in doc.items:
#         bom = frappe.get_all("BOM", filters={"item": item.item_code, "is_active": 1, "is_default": 1})
#         if bom:
#             bom_index = frappe.get_doc("BOM", bom[0].name)
#             item.custom_tsc_cost = bom_index.total_cost
#             item.custom_tsc_cost_with_qty = bom_index.total_cost * item.qty
#             total_cost = total_cost + item.custom_tsc_cost
#             total_cost_with_qty = total_cost_with_qty + item.custom_tsc_cost_with_qty
#         else:
#             item.custom_tsc_cost = item.valuation_rate
#             item.custom_tsc_cost_with_qty = item.valuation_rate * item.qty
#             total_cost = total_cost + item.custom_tsc_cost
#             total_cost_with_qty = total_cost_with_qty + item.custom_tsc_cost_with_qty

#         if item.custom_tsc_cost > 0:
#             item.custom_tsc_margin = item.rate - item.custom_tsc_cost
#             total_margin = total_margin + item.custom_tsc_margin
#             with_qty_margin = item.rate - item.custom_tsc_cost_with_qty
#             total_margin_with_qty = total_margin_with_qty + with_qty_margin

#             if item.custom_tsc_margin > 0:
#                 item.custom_tsc_margin_per = (item.custom_tsc_margin * 100) / item.custom_tsc_cost

#     doc.custom_total_cost = total_cost_with_qty
#     if doc.custom_total_cost > 0 and total_cost_with_qty > 0:
#         doc.custom_total_margin = doc.net_total - total_cost_with_qty
#         doc.custom_margin_percent = (doc.custom_total_margin * 100) / doc.custom_total_cost

# ***moved this code to TSC_sales aug 2025. can remove if no issues *****

# These fields add to a custom field in each of the docs. 

# def add_quote_link(self, event):
# 	if self.custom_tsc_site_visit:
# 		sv = frappe.get_doc("TSC Site Visit", self.custom_tsc_site_visit)
# 		sv.quotation = self.name
# 		sv.status = "Quoting"
# 		sv.save(ignore_permissions=True)
  
# def update_service_call(self, event):
# 	if self.custom_tsc_service_call:
# 		doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
# 		doc.quote = self.name
# 		doc.status = "Quoting"
# 		doc.save(ignore_permissions=True)
#not required as the create quotation is already linking the sales order
  
# def update_service_call_sales_order(self, event):
# 	if self.custom_tsc_service_call:
# 		doc = frappe.get_doc("TSC Service Call", self.custom_tsc_service_call)
# 		doc.sales_order = self.name
# 		doc.save(ignore_permissions=True)
  
# def update_purchase_to_sales(self, event):
# 	if self.custom_sales_order:
# 		doc = frappe.get_doc("Sales Order", self.custom_sales_order)
# 		doc.custom_purchase_order = self.name
# 		doc.save(ignore_permissions=True)


@frappe.whitelist()
def make_quotation(source_name, target_doc=None):
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		#if not source.get("items", []):
		#	quotation.opportunity = source.name

	doclist = get_mapped_doc(
		"TSC Service Call",
		source_name,
		{
			"TSC Service Call": {
				"doctype": "Quotation",
				"field_map": {"customer": "party_name"},
			},
			"TSC Service Call Info": {
				"doctype": "Quotation Item",
				"field_map": {
					"uom": "stock_uom",
				},
				"add_if_empty": True,
			},
		},
		target_doc,
		set_missing_values,
	)

	return doclist





@frappe.whitelist()
def make_quotation_site_visit(source_name, target_doc=None):
	sv = frappe.get_doc("TSC Site Visit", source_name)
	
	cust = frappe.new_doc("Customer")
	if sv.customer_type == "Company":
		cust.customer_name = sv.organization_name
	if sv.customer_type == "Individual":
		cust.customer_name = sv.customer_name

	if not frappe.db.exists("Customer", cust.customer_name):
		cust.customer_group = sv.customer_group
		cust.customer_type = sv.customer_type
		cust.territory = sv.territory
		cust.save(ignore_permissions=True)
		if sv.customer_name:
			cont = frappe.new_doc("Contact")
			cont.first_name = sv.customer_name
			cont.append("phone_nos",{
				"phone": sv.mobile_no,
				"is_primary_mobile_no": 1
			})
			cont.append("links",{
				"link_doctype": "Customer",
				"link_name": cust.name
			})
			cont.is_primary_contact = 1
			cont.save(ignore_permissions=True)
		if sv.address:
			address = frappe.new_doc("Address")
			address.address_title = sv.customer_name
			address.address_type = "Billing"
			address.address_line1 = sv.address
			address.country = "United Arab Emirates"
			address.is_primary_address = 1
			address.city = sv.territory
			address.append("links",{
				"link_doctype": "Customer",
				"link_name": cust.name
			})
			address.save(ignore_permissions=True)
	else:
		# pass
		frappe.throw("Quatation Created Already for this Customer. So No Need to Create!")
		# frappe.throw(title='Error', msg='Same Customer Name exists, please differentiate!')
			
		
		
	def set_missing_values(source, target):
		from erpnext.controllers.accounts_controller import get_default_taxes_and_charges

		quotation = frappe.get_doc(target)

		company_currency = frappe.get_cached_value("Company", quotation.company, "default_currency")

		if company_currency == quotation.currency:
			exchange_rate = 1
		else:
			exchange_rate = get_exchange_rate(
				quotation.currency, company_currency, quotation.transaction_date, args="for_selling"
			)

		quotation.conversion_rate = exchange_rate

		# get default taxes
		taxes = get_default_taxes_and_charges(
			"Sales Taxes and Charges Template", company=quotation.company
		)
		if taxes.get("taxes"):
			quotation.update(taxes)

		quotation.run_method("set_missing_values")
		quotation.run_method("calculate_taxes_and_totals")
		quotation.custom_tsc_site_visit = source.name
		#if not source.get("items", []):
		#	quotation.opportunity = source.name

	if sv.customer_type == "Company":
		doclist = get_mapped_doc(
			"TSC Site Visit",
			source_name,
			{
				
				"TSC Site Visit": {
					"doctype": "Quotation",
					"field_map": {"organization_name": "party_name"},
				},
			
			},
			target_doc,
			set_missing_values,
		)
	if sv.customer_type == "Individual":
		doclist = get_mapped_doc(
			"TSC Site Visit",
			source_name,
			{
				
				"TSC Site Visit": {
					"doctype": "Quotation",
					"field_map": {"customer_name": "party_name"},
				},
			
			},
			target_doc,
			set_missing_values,
		)

	return doclist


@frappe.whitelist()
def make_warranty_claim(source_name, target_doc=None):
	sv = frappe.get_doc("TSC Service Call", source_name)
	doclist = get_mapped_doc(
			"TSC Service Call",
			source_name,
			{
				
				"TSC Service Call": {
					"doctype": "Warranty Claim",
					"field_map": {"customer": "customer", "issue_details":"complaint", "name":"custom_service_call", "sales_order": "custom_sales_order_name"},
				},
			
			},
			target_doc,
		)
	return doclist


def warrenty_claim_sales_order(self, event):
	if (self.custom_sales_order_name):
		if (self.custom_sales_order):
			pass
		else:
			sales_order = frappe.get_doc("Sales Order", self.custom_sales_order_name)
			if (sales_order):
				self.custom_sales_order = sales_order.name


@frappe.whitelist()
def get_contact_query(customer):
	# return customer
	customer1 = customer
	if not customer1:
		return []

	return frappe.db.sql("""
		SELECT 
			contact.name
		FROM 
			`tabContact` contact
		JOIN 
			`tabDynamic Link` links ON links.parent = contact.name
		WHERE 
			links.link_doctype = 'Customer' AND links.link_name = %s
	""", (customer1))


@frappe.whitelist()
def create_sub_po(dt, dn, parent_item, can_item, qty, uom, line_id, supplier):
	c_type = ""
	c_size = ""
	c_model = ""
	c_cost = 0
	c_cut_size = 0
	c_motor = ""
	p_item = frappe.get_doc("Item", parent_item)
	for v in p_item.attributes:
		if v.attribute == "Canopy Type":
			c_type = v.attribute_value
		if v.attribute == "Size":
			c_size = v.attribute_value
		if v.attribute == "Model":
			c_model = v.attribute_value
		if v.attribute == "Motor":
			c_motor = v.attribute_value
	if c_type != "" and c_size != "":
		c_cost = frappe.db.get_value("TSC Stitching table", {"canopy_type":c_type, "canopy_size":c_size}, "no_flap_stitching_cost")
	if c_model != "" and c_motor == "Somfy":
		c_cut_size = frappe.db.get_value("Item Attribute Value", {"parent":"Model", "attribute_value":c_model}, "custom_motor_cut")
	if c_model != "" and c_motor != "Somfy":
		c_cut_size = frappe.db.get_value("Item Attribute Value", {"parent":"Model", "attribute_value":c_model}, "custom_manual_cut")
	
	
	so = frappe.get_doc("Sales Order", dn)
	po = frappe.new_doc("Purchase Order")
	po.company = so.company
	po.is_subcontracted = 1
	po.transaction_date = so.transaction_date
	po.supplier = supplier
	po.schedule_date = so.delivery_date
	part1, part2 = c_size.split('x')
	value1 = int(float(part1) * 100)
	value2 = int(float(part2) * 100)
	po.append("items",{
		"fg_item": can_item,
		"fg_item_qty": qty,
		"item_code": "Stitching",
		"qty": qty,
		"description": "Stitching for awning " + c_model + ". Cut Size: " + str(value1 - c_cut_size) + " x " + str(value2 - 30),
		"uom": uom,
		"rate": c_cost,
		"schedule_date": so.delivery_date,
		"sales_order": so.name,
		"sales_order_item": line_id
	})
	po.taxes_and_charges = "UAE VAT 5% - TSUTCL"
	po.run_method("set_missing_values")
	po.run_method("calculate_taxes_and_totals")
	po.save()
	return po



#updated jul 2025 to handle errors in the bom where a field is not filled in
def update_item_price_based_on_bom():
	allowed_ops = ["", "MAN", "SOM", "LLA"]

	# Fetch all Item Prices where the item has a BOM and belongs to the "Retail" Price List
	item_prices = frappe.get_all(
		"Item Price",
		filters={
			'price_list': 'Retail',
			'item_code': ['in', get_items_with_latest_bom()]
		},
		fields=["name", "item_code"]
	)

	for item_price in item_prices:
		bom_name = frappe.get_value(
			"BOM",
			{"item": item_price.item_code, "is_default": 1, "docstatus": 1},
			"name",
			order_by="creation desc"
		)
		if bom_name:
			bom = frappe.get_doc("BOM", bom_name)

			# Check operation_type before saving
			if hasattr(bom, "operation_type") and bom.operation_type not in allowed_ops:
				frappe.logger().warning(
					f"BOM {bom.name} has invalid operation_type '{bom.operation_type}'. Skipping."
				)
				continue

			bom.update_cost()

			try:
				bom.save()
			except Exception as e:
				frappe.logger().error(f"Failed to save BOM {bom.name}: {e}")

	frappe.db.commit()  # Commit all changes at the end

def get_items_with_latest_bom():
	"""Helper function to get item codes that have an associated latest BOM."""
	# Fetch all BOMs that are not cancelled and order them by item and creation date
	boms = frappe.get_all("BOM", fields=["item", "name", "creation"], filters={'docstatus': 1}, order_by="item, creation desc")
	
	latest_boms = {}
	for bom in boms:
		if bom['item'] not in latest_boms:
			latest_boms[bom['item']] = bom['name']  # Assumes the first BOM for each item is the latest due to sorting
	
	return list(latest_boms.keys())

#updated run_retail_price from items that have a bom
@frappe.whitelist()
def run_retail_update():
	# Execute the function
	enqueue(update_item_price_based_on_bom, queue='long', timeout=6000, is_async=True, job_name='update_item_price_based_on_bom')
	return "Started"


## This is a cron which loops through all products and updated the Custom_average_cost in Item with the Average Cost from the stock ledger  
@frappe.whitelist()
def cron_update_item_average_rate():
	all_item_doc = frappe.get_all("Item", filters={"disabled":0}, fields=["name"])
	if (all_item_doc):
		batch_size = 50  # Adjust batch size based on performance
		for i in range(0, len(all_item_doc), batch_size):
			batch = all_item_doc[i:i + batch_size]
			enqueue(process_batch, items=batch)
			# for i in all_item_doc:
		# 	doc = frappe.get_doc("Item", i.get("name"))
		# 	valuation_rate = frappe.db.sql("""
		# 		SELECT valuation_rate
		# 		FROM `tabStock Ledger Entry`
		# 		WHERE item_code = %s
		# 		ORDER BY posting_date DESC, posting_time DESC
		# 		LIMIT 1
		# 	""", i.get("name"))
		# 	valuation_rate = valuation_rate[0][0] if valuation_rate else 0

		# 	if valuation_rate:
		# 		doc.custom_average_cost = valuation_rate
		# 	else:
		# 		doc.custom_average_cost = 0
		# 	doc.save(ignore_permissions=True)
  
def process_batch(items):
	for i in items:
		item_code = i.get("name")
		valuation_rate = frappe.db.sql("""
			SELECT valuation_rate
			FROM `tabStock Ledger Entry`
			WHERE item_code = %s
			ORDER BY posting_date DESC, posting_time DESC
			LIMIT 1
		""", item_code)
		valuation_rate = valuation_rate[0][0] if valuation_rate else 0

		current = frappe.db.get_value("Item", item_code, "custom_average_cost")
		if current != valuation_rate:
			frappe.db.set_value("Item", item_code, "custom_average_cost", valuation_rate)
   

def epoch_time_ms_to_datetime(epoch_time_ms):
    system_timezone = timezone(get_system_timezone())
    epoch_time = epoch_time_ms / 1000.0
    converted_datetime = datetime.fromtimestamp(epoch_time)
    converted_datetime_in_timezone = converted_datetime.astimezone(system_timezone)
    formatted_datetime = converted_datetime_in_timezone.strftime('%Y-%m-%d %H:%M:%S')
    return formatted_datetime
