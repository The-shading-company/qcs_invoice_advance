import frappe
import json



@frappe.whitelist()
def update_item_price(item_group, contract_price, dealer_price, retail_price, retail_price_list, contract_price_list, dealer_price_list):
	contract_price = json.loads(contract_price)
	dealer_price = json.loads(dealer_price)
	retail_price = json.loads(retail_price)
	item_doc = frappe.get_all("Item", filters={"item_group":item_group, "custom_avoid_auto_update_price_list_based_on_item_group":0},fields=["name", "custom_average_cost", "valuation_rate"])
	if (item_doc):
		for i in item_doc:
		# Contract_price_list
			price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": contract_price_list}, fields=["name"])
			if price_doc:
				for j in price_doc:
					price_doc1 = frappe.get_doc("Item Price", j.get("name"))
					if (i.get("custom_average_cost")):
						if (float(i.get("custom_average_cost")) > 0):
							if (contract_price > 0):
								cost = float(i.get("custom_average_cost")) * contract_price
								price_doc1.price_list_rate = cost
							# else:
							# 	price_doc1.price_list_rate = float(i.get("valuation_rate"))
		  
						else:
							if i.get("valuation_rate"):
								if (i.get("valuation_rate") > 0):
									if (contract_price > 0):
										cost = float(i.get("valuation_rate")) * contract_price
										price_doc1.price_list_rate = cost
									# else:
									# 	cost = float(i.get("valuation_rate"))
									# 	price_doc1.price_list_rate = cost
					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (contract_price > 0):
									cost = float(i.get("valuation_rate")) * contract_price
									price_doc1.price_list_rate = cost
								# else:
								# 	cost = float(i.get("valuation_rate"))
								# 	price_doc1.price_list_rate = cost
					price_doc1.save(ignore_permissions=True)
		
			else:
				final_cost = []
				if (i.get("custom_average_cost")):
					if (float(i.get("custom_average_cost")) > 0):
						if (contract_price > 0):
							cost = float(i.get("custom_average_cost")) * contract_price
							final_cost.append(cost)
						# else:
						# 	if (i.get("valuation_rate")):
						# 		final_cost.append(float(i.get("valuation_rate")))

					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (contract_price > 0):
									final_cost.append(float(i.get("valuation_rate"))*contract_price)
								# else:
								# 	final_cost.append(float(i.get("valuation_rate")))
				else:
					if i.get("valuation_rate"):
						if (i.get("valuation_rate") > 0):
							if (contract_price > 0):
								final_cost.append(float(i.get("valuation_rate"))*contract_price)
							# else:
							# 	final_cost.append(float(i.get("valuation_rate")))
				
				if final_cost:
					create_price_doc = frappe.new_doc("Item Price")
					create_price_doc.update({
						"item_code": i.get("name"),
						"price_list": contract_price_list,
						"price_list_rate": final_cost[0] or 0
					})
					create_price_doc.save(ignore_permissions=True)
	
	# dealer_price_list
			price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": dealer_price_list}, fields=["name"])
			if price_doc:
				for j in price_doc:
					price_doc1 = frappe.get_doc("Item Price", j.get("name"))
					if (i.get("custom_average_cost")):
						if (float(i.get("custom_average_cost")) > 0):
							if (price_doc1.price_list == dealer_price_list):
								if (dealer_price > 0):
									cost = float(i.get("custom_average_cost")) * dealer_price
									price_doc1.price_list_rate = cost
								# else:
								# 	if (i.get("valuation_rate")):
								# 		if (i.get("valuation_rate") > 0):
								# 			price_doc1.price_list_rate = float(i.get("valuation_rate"))
						else:
							if i.get("valuation_rate"):
								if (i.get("valuation_rate") > 0):
									if (dealer_price > 0):
										cost = float(i.get("valuation_rate")) * dealer_price
										price_doc1.price_list_rate = cost
									# else:
									# 	cost = float(i.get("valuation_rate"))
									# 	price_doc1.price_list_rate = cost
					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (dealer_price > 0):
									cost = float(i.get("valuation_rate")) * dealer_price
									price_doc1.price_list_rate = cost
								# else:
								# 	cost = float(i.get("valuation_rate"))
								# 	price_doc1.price_list_rate = cost
					price_doc1.save(ignore_permissions=True)
		
			else:
				final_cost1 = []
				if (i.get("custom_average_cost")):
					if (float(i.get("custom_average_cost")) > 0):
						if (dealer_price > 0):
							cost = float(i.get("custom_average_cost")) * dealer_price
							final_cost1.append(cost)
						# else:
						# 	if (i.get("valuation_rate")):
						# 		if (i.get("valuation_rate") > 0):
						# 			final_cost1.append(float(i.get("valuation_rate")))
							
					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (dealer_price > 0):
									final_cost1.append(float(i.get("valuation_rate")) * dealer_price)
								# else:
								# 	final_cost1.append(float(i.get("valuation_rate")))
				else:
					if i.get("valuation_rate"):
						if (i.get("valuation_rate") > 0):
							if (dealer_price > 0):
								final_cost1.append(float(i.get("valuation_rate")) * dealer_price)
							# else:
							# 	final_cost1.append(float(i.get("valuation_rate")))
		
				if final_cost1:
					create_price_doc = frappe.new_doc("Item Price")
					create_price_doc.update({
						"item_code": i.get("name"),
						"price_list": dealer_price_list,
						"price_list_rate": final_cost1[0] or 0
					})
					create_price_doc.save(ignore_permissions=True)
	
	# retail_price_list
			price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": retail_price_list}, fields=["name"])
			if price_doc:
				for j in price_doc:
					price_doc1 = frappe.get_doc("Item Price", j.get("name"))
					if (i.get("custom_average_cost")):
						if (float(i.get("custom_average_cost")) > 0):
							if (price_doc1.price_list == retail_price_list):
								if (retail_price > 0):
									cost = float(i.get("custom_average_cost")) * retail_price
									price_doc1.price_list_rate = cost
								# else:
								# 	if (i.get("valuation_rate")):
								# 		if (i.get("valuation_rate") > 0):
								# 			price_doc1.price_list_rate = float(i.get("valuation_rate"))
		  
						else:
							if i.get("valuation_rate"):
								if (i.get("valuation_rate") > 0):
									if (retail_price > 0):
										cost = float(i.get("valuation_rate")) * retail_price
										price_doc1.price_list_rate = cost
									# else:
									# 	cost = float(i.get("valuation_rate"))
									# 	price_doc1.price_list_rate = cost
					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (retail_price > 0):
									cost = float(i.get("valuation_rate")) * retail_price
									price_doc1.price_list_rate = cost
								# else:
								# 	cost = float(i.get("valuation_rate"))
								# 	price_doc1.price_list_rate = cost
					price_doc1.save(ignore_permissions=True)
		
			else:
				final_cost2 = []
				if (i.get("custom_average_cost")):
					if (float(i.get("custom_average_cost")) > 0):
						if (retail_price > 0):
							cost = float(i.get("custom_average_cost")) * retail_price
							final_cost2.append(cost)
						# else:
						# 	if (i.get("valuation_rate")):
						# 		if (i.get("valuation_rate") > 0):
						# 			final_cost2.append(float(i.get("valuation_rate")))
		
					else:
						if i.get("valuation_rate"):
							if (i.get("valuation_rate") > 0):
								if (retail_price > 0):
									final_cost2.append(float(i.get("valuation_rate")) * retail_price)
								# else:
								# 	final_cost2.append(float(i.get("valuation_rate")))
				else:
					if i.get("valuation_rate"):
						if (i.get("valuation_rate") > 0):
							if (retail_price > 0):
								final_cost2.append(float(i.get("valuation_rate")) * retail_price)
							# else:
							# 	final_cost2.append(float(i.get("valuation_rate")))
				if final_cost2:
					create_price_doc = frappe.new_doc("Item Price")
					create_price_doc.update({
						"item_code": i.get("name"),
						"price_list": retail_price_list,
						"price_list_rate": final_cost2[0] or 0
					})
					create_price_doc.save(ignore_permissions=True)
	
		frappe.msgprint("Item Price List Updated.")
  
	else:
		frappe.msgprint("Item Not Found")
  
  
  

@frappe.whitelist()
def item_price_list(item_code, price_list):
	item_doc = frappe.get_doc("Item", item_code)
	if (item_doc.custom_avoid_auto_update_price_list_based_on_item_group == 0):
		item_group_doc = frappe.get_doc("Item Group", item_doc.item_group)
		if (item_doc.custom_average_cost):
			if (float(item_doc.custom_average_cost) > 0):
				if (price_list == item_group_doc.custom_contract_price_list):
					if (item_group_doc.custom_contract_price > 0):
						cost = float(item_doc.custom_average_cost) * item_group_doc.custom_contract_price
						return cost
					# else:
					# 	if item_doc.valuation_rate:
					# 		cost = float(item_doc.valuation_rate)
					# 		return cost
					# 	else:
					# 		return 0	
				if (price_list == item_group_doc.custom_dealer_price_list):
					frappe.errprint(item_group_doc.custom_dealer_price)
					if (item_group_doc.custom_dealer_price > 0):
						frappe.errprint(item_group_doc.custom_dealer_price)
						cost = float(item_doc.custom_average_cost) * item_group_doc.custom_dealer_price
						return cost
					# else:
					# 	if item_doc.valuation_rate:
					# 		cost = float(item_doc.valuation_rate)
					# 		return cost
					# 	else:
					# 		return 0	
				if (price_list == item_group_doc.custom_retail_price_list):
					frappe.errprint(item_group_doc.custom_retail_price)
					if (item_group_doc.custom_retail_price_list > 0):
						frappe.errprint(item_group_doc.custom_retail_price)
						cost = float(item_doc.custom_average_cost) * item_group_doc.custom_retail_price
						return cost
					# else:
					# 	if item_doc.valuation_rate:
					# 		cost = float(item_doc.valuation_rate)
					# 		return cost
					# 	else:
					# 		return 0	
			else:
				if item_doc.valuation_rate:
					if item_doc.valuation_rate > 0:
						if (price_list == item_group_doc.custom_contract_price_list):
							if (item_group_doc.custom_contract_price > 0):
								cost = float(item_doc.valuation_rate) * item_group_doc.custom_contract_price
								return cost	
						if (price_list == item_group_doc.custom_dealer_price_list):
							if (item_group_doc.custom_dealer_price > 0):
								cost = float(item_doc.valuation_rate) * item_group_doc.custom_dealer_price
								return cost
						if (price_list == item_group_doc.custom_retail_price_list):
							if (item_group_doc.custom_dealer_price > 0):
								cost = float(item_doc.valuation_rate) * item_group_doc.custom_retail_price
								return cost	

		else:
			if item_doc.valuation_rate:
				if item_doc.valuation_rate > 0:
					if (price_list == item_group_doc.custom_contract_price_list):
						if (item_group_doc.custom_contract_price > 0):
							cost = float(item_doc.valuation_rate) * item_group_doc.custom_contract_price
							return cost	
					if (price_list == item_group_doc.custom_dealer_price_list):
						if (item_group_doc.custom_dealer_price > 0):
							cost = float(item_doc.valuation_rate) * item_group_doc.custom_dealer_price
							return cost	
					if (price_list == item_group_doc.custom_retail_price_list):
						if (item_group_doc.custom_dealer_price > 0):
							cost = float(item_doc.valuation_rate) * item_group_doc.custom_retail_price
							return cost	
	
  
@frappe.whitelist()
def crom_update_item_price():
	all_item_group = frappe.get_all("Item Group", fields=["name"])
	if all_item_group:
		for g in all_item_group:
			item_group_doc = frappe.get_doc("Item Group", g.get("name"))
			item_group = item_group_doc.name
			contract_price = item_group_doc.custom_contract_price
			dealer_price = item_group_doc.custom_dealer_price
			retail_price = item_group_doc.custom_retail_price
			retail_price_list = item_group_doc.custom_retail_price_list
			contract_price_list = item_group_doc.custom_contract_price_list
			dealer_price_list = item_group_doc.custom_dealer_price_list

			item_doc = frappe.get_all("Item", filters={"item_group":item_group, "custom_avoid_auto_update_price_list_based_on_item_group":0},fields=["name", "custom_average_cost", "valuation_rate"])
			if (item_doc):
				for i in item_doc:
				# Contract_price_list
					if (contract_price_list):
						price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": contract_price_list}, fields=["name"])
						if price_doc:
							for j in price_doc:
								price_doc1 = frappe.get_doc("Item Price", j.get("name"))
								if (i.get("custom_average_cost")):
									if (float(i.get("custom_average_cost")) > 0):
										if (price_doc1.price_list == contract_price_list):
											if (contract_price > 0):
												cost = float(i.get("custom_average_cost")) * contract_price
												price_doc1.price_list_rate = cost
											# else:
											# 	if (i.get("valuation_rate")):
											# 		price_doc1.price_list_rate = float(i.get("valuation_rate"))
					
									else:
										if i.get("valuation_rate"):
											if i.get("valuation_rate") > 0:
												if (contract_price > 0):
													cost = float(i.get("valuation_rate")) * contract_price
													price_doc1.price_list_rate = cost
												# else:
												# 	cost = float(i.get("valuation_rate"))
												# 	price_doc1.price_list_rate = cost
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (contract_price > 0):
												cost = float(i.get("valuation_rate")) * contract_price
												price_doc1.price_list_rate = cost
											# else:
											# 	cost = float(i.get("valuation_rate"))
											# 	price_doc1.price_list_rate = cost
								price_doc1.save(ignore_permissions=True)
					
						else:
							final_cost = []
							if (i.get("custom_average_cost")):
								if (float(i.get("custom_average_cost")) > 0):
									if (contract_price > 0):
										cost = float(i.get("custom_average_cost")) * contract_price
										final_cost.append(cost)
									# else:
									# 	if (i.get("valuation_rate")):
									# 		final_cost.append(float(i.get("valuation_rate")))
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (contract_price > 0):
												final_cost.append(float(i.get("valuation_rate")) * contract_price)
											# else:
											# 	final_cost.append(float(i.get("valuation_rate")))
							else:
								if i.get("valuation_rate"):
									if i.get("valuation_rate") > 0:
										if (contract_price > 0):
											final_cost.append(float(i.get("valuation_rate")) * contract_price)
										# else:
										# 	final_cost.append(float(i.get("valuation_rate")))
								
							if final_cost:
								create_price_doc = frappe.new_doc("Item Price")
								create_price_doc.update({
									"item_code": i.get("name"),
									"price_list": contract_price_list,
									"price_list_rate": final_cost[0] or 0
								})
								create_price_doc.save(ignore_permissions=True)
			
			# dealer_price_list
					if dealer_price_list:
						price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": dealer_price_list}, fields=["name"])
						if price_doc:
							for j in price_doc:
								price_doc1 = frappe.get_doc("Item Price", j.get("name"))
								if (i.get("custom_average_cost")):
									if (float(i.get("custom_average_cost")) > 0):
										if (price_doc1.price_list == dealer_price_list):
											if (dealer_price > 0):
												cost = float(i.get("custom_average_cost")) * dealer_price
												price_doc1.price_list_rate = cost
											# else:
											# 	if (i.get("valuation_rate")):
											# 		price_doc1.price_list_rate = float(i.get("valuation_rate"))
					
									else:
										if i.get("valuation_rate"):
											if i.get("valuation_rate") > 0:
												if (dealer_price > 0):
													cost = float(i.get("valuation_rate")) * dealer_price
													price_doc1.price_list_rate = cost
												# else:
												# 	cost = float(i.get("valuation_rate"))
												# 	price_doc1.price_list_rate = cost
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (dealer_price > 0):
												cost = float(i.get("valuation_rate")) * dealer_price
												price_doc1.price_list_rate = cost
											# else:
											# 	cost = float(i.get("valuation_rate"))
											# 	price_doc1.price_list_rate = cost
								price_doc1.save(ignore_permissions=True)
					
						else:
							final_cost1 = []
							if (i.get("custom_average_cost")):
								if (float(i.get("custom_average_cost")) > 0):
									if (dealer_price > 0):
										cost = float(i.get("custom_average_cost")) * dealer_price
										final_cost1.append(cost)
									# else:
									# 	if (i.get("valuation_rate")):
									# 		final_cost1.append(float(i.get("valuation_rate")))
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (dealer_price > 0):
												final_cost1.append(float(i.get("valuation_rate"))*dealer_price)
											# else:
											# 	final_cost1.append(float(i.get("valuation_rate")))
							else:
								if i.get("valuation_rate"):
									if i.get("valuation_rate") > 0:
										if (dealer_price > 0):
											final_cost1.append(float(i.get("valuation_rate"))*dealer_price)
										# else:
										# 	final_cost1.append(float(i.get("valuation_rate")))
				
							if final_cost1:
								create_price_doc = frappe.new_doc("Item Price")
								create_price_doc.update({
									"item_code": i.get("name"),
									"price_list": dealer_price_list,
									"price_list_rate": final_cost1[0] or 0
								})
								create_price_doc.save(ignore_permissions=True)
			
			# retail_price_list
					if retail_price_list:
						price_doc = frappe.get_all("Item Price", filters={"item_code": i.get("name"), "price_list": retail_price_list}, fields=["name"])
						if price_doc:
							for j in price_doc:
								price_doc1 = frappe.get_doc("Item Price", j.get("name"))
								if (i.get("custom_average_cost")):
									if (float(i.get("custom_average_cost")) > 0):
										if (price_doc1.price_list == retail_price_list):
											if (retail_price > 0):
												cost = float(i.get("custom_average_cost")) * retail_price
												price_doc1.price_list_rate = cost
											# else:
											# 	if (i.get("valuation_rate")):
											# 		price_doc1.price_list_rate = float(i.get("valuation_rate"))
					
									else:
										if i.get("valuation_rate"):
											if i.get("valuation_rate") > 0:
												if (retail_price > 0):
													cost = float(i.get("valuation_rate")) * retail_price
													price_doc1.price_list_rate = cost
												# else:
												# 	cost = float(i.get("valuation_rate"))
												# 	price_doc1.price_list_rate = cost
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (retail_price > 0):
												cost = float(i.get("valuation_rate")) * retail_price
												price_doc1.price_list_rate = cost
											# else:
											# 	cost = float(i.get("valuation_rate"))
											# 	price_doc1.price_list_rate = cost
								price_doc1.save(ignore_permissions=True)
					
						else:
							final_cost2 = []
							if (i.get("custom_average_cost")):
								if (float(i.get("custom_average_cost")) > 0):
									if (retail_price > 0):
										cost = float(i.get("custom_average_cost")) * retail_price
										final_cost2.append(cost)
									# else:
									# 	if (i.get("valuation_rate")):
									# 		final_cost2.append(float(i.get("valuation_rate")))
					
								else:
									if i.get("valuation_rate"):
										if i.get("valuation_rate") > 0:
											if (retail_price > 0):
												final_cost2.append(float(i.get("valuation_rate"))* retail_price)
											# else:
											# 	final_cost2.append(float(i.get("valuation_rate")))
							else:
								if i.get("valuation_rate"):
									if i.get("valuation_rate") > 0:
										if (retail_price > 0):
											final_cost2.append(float(i.get("valuation_rate"))* retail_price)
										# else:
										# 	final_cost2.append(float(i.get("valuation_rate")))
							if final_cost2:
								create_price_doc = frappe.new_doc("Item Price")
								create_price_doc.update({
									"item_code": i.get("name"),
									"price_list": retail_price_list,
									"price_list_rate": final_cost2[0] or 0
								})
								create_price_doc.save(ignore_permissions=True)
			
				frappe.msgprint("Item Price List Updated.")
		
			else:
				frappe.msgprint("Item Not Found")