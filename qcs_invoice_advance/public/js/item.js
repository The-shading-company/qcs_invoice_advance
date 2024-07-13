frappe.ui.form.on('Item', {
    custom_woo_update: function(frm) {
		if (cur_frm.doc.custom_woovariationid){
			if(cur_frm.doc.custom_online == 1 && cur_frm.doc.custom_woovariation == 1 && cur_frm.doc.custom_woovariationid && cur_frm.doc.custom_wooid){
				frappe.call({
					method: "qcs_invoice_advance.controller.item_api.woo_update_variant_item",
					args: {
						"wooid": cur_frm.doc.custom_wooid,
						"woovariationid": cur_frm.doc.custom_woovariationid,
						"item_code": cur_frm.doc.name
					},
				});
			}
		}
		else{
			if(cur_frm.doc.custom_online == 1 && cur_frm.doc.custom_wooid){
				frappe.call({
					method: "qcs_invoice_advance.controller.item_api.woo_update_normal_item",
					args: {
						"wooid": cur_frm.doc.custom_wooid,
						"item_code": cur_frm.doc.name
					},
				});
			}
		}
	// 	if(cur_frm.doc.variant_of){
	// 		if(cur_frm.doc.custom_online == 1 && cur_frm.doc.custom_woovariation == 1 && cur_frm.doc.custom_woovariationid && cur_frm.doc.custom_wooid){
	// 			frappe.call({
	// 				method: "qcs_invoice_advance.controller.item_api.woo_update_variant_item",
	// 				args: {
	// 					"wooid": cur_frm.doc.custom_wooid,
	// 					"woovariationid": cur_frm.doc.custom_woovariationid,
	// 					"item_code": cur_frm.doc.name
	// 				},
	// 			});
	// 		}
	// 		else{
	// 			frappe.msgprint("This is Variant Item Make Sure the Woo Section.")
	// 		}
	// 	}
	// 	else{
	// 		if (cur_frm.doc.has_variants == 0){
	// 			if(cur_frm.doc.custom_online == 1 && cur_frm.doc.custom_wooid){
	// 				frappe.call({
	// 					method: "qcs_invoice_advance.controller.item_api.woo_update_normal_item",
	// 					args: {
	// 						"wooid": cur_frm.doc.custom_wooid,
	// 						"item_code": cur_frm.doc.name
	// 					},
	// 				});
	// 			}
	// 		}
	// 		if (cur_frm.doc.has_variants == 1){
	// 			if(cur_frm.doc.custom_online == 1 && cur_frm.doc.custom_woovariation == 1 && cur_frm.doc.custom_woovariationid && cur_frm.doc.custom_wooid){
	// 				frappe.call({
	// 					method: "qcs_invoice_advance.controller.item_api.woo_update_variant_item",
	// 					args: {
	// 						"wooid": cur_frm.doc.custom_wooid,
	// 						"woovariationid": cur_frm.doc.custom_woovariationid,
	// 						"item_code": cur_frm.doc.name
	// 					},
	// 				});
	// 			}
	// 			else{
	// 				frappe.msgprint("This is Variant Item Make Sure the Woo Section.")
	// 			}
	// 		}

	// 	}
        
		
    }
});