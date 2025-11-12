frappe.ui.form.on('TSC Service Call', {
    refresh: function(frm) {
    },
    
    validate: function(frm){
        var total = 0;
        $.each(frm.doc.table_sxqn,  function(i,  d) {
            
            // calculate incentive
            d.amount = d.rate * d.qty;
            total += d.rate * d.qty;
            // actual incentive
        });
        frm.doc.total = total;
    },
    customer: function(frm){
        if (frm.doc.customer) {
            frappe.call({
                method: "qcs_invoice_advance.controller.item.get_contact_query",
                args: {
                    "customer": frm.doc.customer,
                },
                callback: function(r) {
                    console.log(r.message)
                    if (r.message) {
                        var contacts = r.message.map(contact => contact[0]);
                        frm.set_query('contact', function() {
                            return {
                                filters: {
                                    'name': ['in', contacts]
                                }
                            };
                        });
                        frm.refresh_field('contact');
                    }
                }
            });
        }
    }  
    
});

//function create_quotation(frm) {
    // You can fetch data from the Issue and use it in the Quotation
 //   var customer = frm.doc.customer;
  //  var issue_details = frm.doc.description;

    // Create a new Quotation document
  //  if (cur_frm.doc.status_time_log && cur_frm.doc.status_time_log.length > 0){
  //      frappe.model.open_mapped_doc({
  //          method: "qcs_invoice_advance.controller.item.make_quotation",
  //          frm: frm
  //      });
  //  }
  //  else{
  //      frappe.throw("Previous Status(Arranging Site Visit) Missing in Status Time Log Table")
  //  }
//}





// calculates the total in the repair table
frappe.ui.form.on('TSC Service Call Info', {

        item_code: function(frm, cdt, cdn) 
            { 
		var d = locals[cdt][cdn];
                console.log("Item Code: " + d.item_code);
                frappe.call(
                    { 
                        method: "frappe.client.get_value",
                        args: { 
                            doctype: "Item Price", 
                            filters: {
                                price_list: frm.doc.price_list, 
                                item_code: d.item_code
                            },
                            fieldname:["price_list_rate"]
                        },
                        callback: function(r) 
                            { 
                                if(r.message) 
                                    { 
                                        var item_price = r.message; 
                                        d.rate = item_price.price_list_rate;
                                        d.amount = d.qty * d.rate;
                                    } 
                            }
                    });   
            } 
    }
);

frappe.ui.form.on('TSC Service Call', {
    refresh: function(frm) {
        // Check if the status is 'Arranging Site Visit' before adding the button
        if (frm.doc.status === 'Arranging Site Visit') {
            frm.add_custom_button('Send Service Call SMS', function() {
                const mobile_no = frm.doc.mob_no; // Ensure this is the correct field ID for the mobile number
                const svcall_no = frm.doc.name;
                const message = "Hello, your service call has been scheduled. " + svcall_no + " Our service team will contact you with 2-3 days to schedule your appointment."; // Customize your message here

                if (mobile_no) {
                    frappe.call({
                        method: "frappe.core.doctype.sms_settings.sms_settings.send_sms",
                        args: {
                            receiver_list: [mobile_no],
                            msg: message
                        },
                        callback: function(r) {
                            if (r.exc) {
                                frappe.msgprint(r.exc);
                                return;
                            }
                            console.log('SMS Sent:', message);
                            frappe.msgprint('SMS sent successfully to ' + mobile_no);
                            // Adding a comment
                            add_comment_to_doc(frm, message);
                        }
                    });
                } else {
                    frappe.msgprint('No valid mobile number found.');
                }
            });
        }
    }
});

function add_comment_to_doc(frm, message) {
    // Create a new Comment doc
    var comment = frappe.model.get_new_doc('Comment');
    comment.comment_type = "Info"; // Use "Info" for general information comments
    comment.comment_email = frappe.session.user.email;
    comment.content = "User sent an SMS with the following text: " + message;
    comment.reference_doctype = "TSC Service Call";
    comment.reference_name = frm.doc.name;

    // Save the comment
    frappe.call({
        method: "frappe.client.insert",
        args: {
            doc: comment
        },
        callback: function(r) {
            if (!r.exc) {
                frappe.msgprint('Comment added successfully.');
                frm.reload_doc(); // This will refresh the whole document and show the new comment
            } else {
                frappe.msgprint('Failed to add comment: ' + r.exc);
            }
        }
    });
}
