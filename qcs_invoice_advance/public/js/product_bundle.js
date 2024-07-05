frappe.ui.form.on('Product Bundle Item', {
    item_code(frm, cdt, cdn){
        var row = locals[cdt][cdn];
        if (row.item_code){
            frappe.call({
                method: "qcs_invoice_advance.controller.product_bundle.bundle_item_stock",
                args: {
                    "item_code": row.item_code,
                },
                callback: function (r) {
                    frappe.model.set_value(cdt, cdn, 'custom_in_stock', r.message);
                },
            });
        }
    },
    qty(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        if (row.custom_average_rate>0){
            let custom_cost1 = row.custom_average_rate * row.qty;
            frappe.model.set_value(cdt, cdn, 'custom_item_cost', custom_cost1);
        }
        else{
            let custom_cost1 = row.custom_item_validation_rate * row.qty;
            frappe.model.set_value(cdt, cdn, 'custom_item_cost', custom_cost1);
        }

    },
 });