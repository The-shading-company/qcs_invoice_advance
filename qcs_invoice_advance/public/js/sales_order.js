frappe.ui.form.on('Sales Order', {
   
	refresh: function(frm) {
        if(frm.doc.docstatus==1){
            frm.add_custom_button(__('Partial Invoice'), () => {
                var d = new frappe.ui.Dialog({
                    title: __('Invoice Percentage'),
                    fields: [
                        {
                            "label" : "Percentage to Invoice",
                            "fieldname": "per",
                            "fieldtype": "Percent",
                            "reqd": 1,
                            "default": 0
                        }
                    ],
                    primary_action: function() {
                        var data = d.get_values();
                        let total_per = data.per + frm.doc.partial_invoice
                        if (total_per <= 0 || total_per > 100) {
                            frappe.msgprint(__('Invalid percentage. Check Partial Invoice %'));
                            return;
                        }
                        frappe.call({
                            method: 'qcs_invoice_advance.controller.sales_order.create_partial_invoice',
                            args: {
                                sales_order: frm.doc.name,
                                percentage: data.per
                            },
                            callback: function(r) {
                                frappe.set_route('Form', 'Sales Invoice', r.message);
                                d.hide();
                            
                            }
                        });
                    },
                    primary_action_label: __('Create Invoice')
                });
                d.show();
                
            }, __("Create"));
        }
        
    }
   
});