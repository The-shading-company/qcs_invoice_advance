frappe.ui.form.on('Item Price', {
    price_list: function(frm) {
        frappe.call({
            method: "qcs_invoice_advance.controller.item.item_price_list",
            args: {
                "item_code": cur_frm.doc.item_code,
                "price_list": cur_frm.doc.price_list
            },
            callback: function(r) {
                if(r.message) {
                    frm.set_value('price_list_rate', r.message);
                }
                else{
                    frm.set_value('price_list_rate', 0);
                }
            }
        })
    }
});