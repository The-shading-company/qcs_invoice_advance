# Copyright (c) 2024, Quark Cyber Systems FZC and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	if not filters:
		filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data


def get_columns(filters):
	columns = [
		{
			"label": "Customer",
			"fieldname": "customer",
			"fieldtype": "Link",
			"options": "Customer",
			"width": 200,
		},
		{
			"label": "Customer Name",
			"fieldname": "customer_name",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Telephone / mobilenumber",
			"fieldname": "phone",
			"fieldtype": "Data",
			"width": 200,
		},
		{
			"label": "Address",
			"fieldname": "add",
			"fieldtype": "Data",
			"width": 200,
		},
	]
	return columns




# def get_data(filters):
# 	duplicates = []
# 	if (filters.get("customer")):
# 		customers = frappe.get_all("Customer", filter={"name":filters.get("customer")}, fields=["name", "customer_name", "mobile_no", "customer_primary_address"])
# 		customer_name_dict = {}
# 		duplicates = []

# 		for customer in customers:
# 			normalized_customer_name = customer.customer_name.replace(" ", "").lower()
			
# 			if normalized_customer_name in customer_name_dict:
# 				duplicates.append({
# 					"customer": customer.name,
# 					"customer_name": customer.customer_name,
# 					"phone": customer.mobile_no,
# 					"address": customer.customer_primary_address
# 				})
# 				if customer_name_dict[normalized_customer_name] is not None:
# 					duplicates.append(customer_name_dict[normalized_customer_name])
# 					customer_name_dict[normalized_customer_name] = None
# 			else:
# 				customer_name_dict[normalized_customer_name] = {
# 					"customer": customer.name,
# 					"customer_name": customer.customer_name,
# 					"phone": customer.mobile_no,
# 					"address": customer.customer_primary_address
# 				}
# 	else:
# 		customers = frappe.get_all("Customer", fields=["name", "customer_name", "mobile_no", "customer_primary_address"])
# 		customer_name_dict = {}
# 		duplicates = []

# 		for customer in customers:
# 			normalized_customer_name = customer.customer_name.replace(" ", "").lower()
			
# 			if normalized_customer_name in customer_name_dict:
# 				duplicates.append({
# 					"customer": customer.name,
# 					"customer_name": customer.customer_name,
# 					"phone": customer.mobile_no,
# 					"address": customer.customer_primary_address
# 				})
# 				if customer_name_dict[normalized_customer_name] is not None:
# 					duplicates.append(customer_name_dict[normalized_customer_name])
# 					customer_name_dict[normalized_customer_name] = None
# 			else:
# 				customer_name_dict[normalized_customer_name] = {
# 					"customer": customer.name,
# 					"customer_name": customer.customer_name,
# 					"phone": customer.mobile_no,
# 					"address": customer.customer_primary_address
# 				}
			

# 	frappe.errprint(duplicates)
# 	return duplicates


def get_data(filters):
	duplicates = []
	
	customers = frappe.get_all("Customer", fields=["name", "customer_name", "mobile_no", "customer_primary_address"])

	customer_name_dict = {}
	customer_phone_dict = {}

	for customer in customers:
		# Normalize customer name by removing spaces and converting to lowercase
		normalized_customer_name = customer.customer_name.replace(" ", "").lower()
		# Normalize phone number by removing spaces and hyphens, if it exists
		normalized_phone_no = customer.mobile_no.replace(" ", "").replace("-", "") if customer.mobile_no else None
		
		# Check for duplicates based on customer name
		if normalized_customer_name in customer_name_dict:
			duplicates.append({
				"customer": customer.name,
				"customer_name": customer.customer_name,
				"phone": customer.mobile_no,
				"address": customer.customer_primary_address
			})
			if customer_name_dict[normalized_customer_name] is not None:
				duplicates.append(customer_name_dict[normalized_customer_name])
				customer_name_dict[normalized_customer_name] = None
		else:
			customer_name_dict[normalized_customer_name] = {
				"customer": customer.name,
				"customer_name": customer.customer_name,
				"phone": customer.mobile_no,
				"address": customer.customer_primary_address
			}
		
		# Check for duplicates based on phone number if phone number is available
		if normalized_phone_no:
			if normalized_phone_no in customer_phone_dict:
				duplicates.append({
					"customer": customer.name,
					"customer_name": customer.customer_name,
					"phone": customer.mobile_no,
					"address": customer.customer_primary_address
				})
				if customer_phone_dict[normalized_phone_no] is not None:
					duplicates.append(customer_phone_dict[normalized_phone_no])
					customer_phone_dict[normalized_phone_no] = None
			else:
				customer_phone_dict[normalized_phone_no] = {
					"customer": customer.name,
					"customer_name": customer.customer_name,
					"phone": customer.mobile_no,
					"address": customer.customer_primary_address
			}

	frappe.errprint(duplicates)
	return duplicates