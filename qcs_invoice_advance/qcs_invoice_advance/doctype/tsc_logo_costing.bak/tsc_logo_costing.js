// Copyright (c) 2024, Quark Cyber Systems FZC and contributors
// For license information, please see license.txt

frappe.ui.form.on("TSC Logo Costing", {
	refresh(frm) {
        if (!frm.is_new()) {
            if (cur_frm.doc.logos.length > 0){
                let any_item_without_web_link = frm.doc.logos.some(logo_tab => !logo_tab.costing_link);
                if (any_item_without_web_link){
                    frm.add_custom_button(__("Create Web Form Link"), function () {
                        let any_item_without_supplier = frm.doc.logos.some(logo_tab => !logo_tab.supplier);
                        if (any_item_without_supplier){
                            frappe.throw("Supplier is Missing.")
                        }
                        let any_item_without_logo_details = frm.doc.logos.some(logo_tab => !logo_tab.logo_details);
                        if (any_item_without_logo_details){
                            frappe.throw("Logo Detail is Missing.")
                        }
                        frappe.call({
                            method:"qcs_invoice_advance.qcs_invoice_advance.doctype.tsc_logo_costing.tsc_logo_costing.make_web_from_link",
                            args:{
                                "name": cur_frm.doc.name,
                            },
                        })
                    })
                }
            }
        }
        if (cur_frm.doc.logos.length > 0){
            let any_item_with_web_link = frm.doc.logos.some(logo_tab => logo_tab.costing_link);
            if (any_item_with_web_link){
                let any_item_without_send_email = frm.doc.logos.some(logo_tab => logo_tab.sent_email!=1);
                if (any_item_without_send_email){
                    frm.add_custom_button(__("Send Email"), function () {
                        frappe.call({
                            method:"qcs_invoice_advance.qcs_invoice_advance.doctype.tsc_logo_costing.tsc_logo_costing.send_email_to_supplier",
                            args:{
                                "tab": cur_frm.doc.logos,
                                "name": cur_frm.doc.name
                            },
                        })
                    })
                }
            }
            let any_item_without_logo_unit_cost= frm.doc.logos.some(logo_tab => logo_tab.logo_unit_cost == 0);
            if (any_item_without_logo_unit_cost){
                frm.set_value("status", "Awaiting Price")
            }
            else{
                frm.set_value("status", "Recieved")
                frm.save();
            }
        }
	},
    custom_send_link_via_whats_app_to_supplier: function(frm) {
        // Fetching the costing_link from the child table 'logos'
        let costing_links = [];
        frm.doc.logos.forEach(function(row) {
            if (row.costing_link) {
                costing_links.push(row.costing_link);
            }
        });

        if (costing_links.length > 0) {
            // Assuming you have a specific number to send the message to
            //let phoneNumber = '971559994750';  // Replace with the actual phone number

            // Custom message
            //let customMessage = "Please can you let us know the price for this logo. Thanks. ";
            //let message = customMessage + costing_links.join(', ');

            // Generate WhatsApp web link
            //let whatsappLink = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;

            // Open WhatsApp web link in a new tab/window
            //window.open(whatsappLink, '_blank');
        } else {
            frappe.msgprint(__('No costing links found.'));
        }
    }
});

