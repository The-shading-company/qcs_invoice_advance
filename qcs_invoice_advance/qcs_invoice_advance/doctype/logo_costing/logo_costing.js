// Copyright (c) 2024, Quark Cyber Systems FZC and contributors
// For license information, please see license.txt

frappe.ui.form.on("Logo Costing", {
	refresh(frm) {
        if (!frm.is_new()) {
            if (cur_frm.doc.logos.length > 0){
                let any_item_without_web_link = frm.doc.logos.some(logo_tab => !logo_tab.costing_link);
                if (any_item_without_web_link){
                    frm.add_custom_button(__("Create Web Form Link"), function () {
                        frappe.call({
                            method:"qcs_invoice_advance.qcs_invoice_advance.doctype.logo_costing.logo_costing.make_web_from_link",
                            args:{
                                "name": cur_frm.doc.name,
                            },
                        })
                    })
                }
            }
        }
	},
});
