frappe.ui.form.on('Product Bundle Item', {
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