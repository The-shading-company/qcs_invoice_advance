frappe.ui.form.on('Product Bundle Item', {
    // item_code(frm, cdt, cdn) {
    //     console.log("jjhhh")
        // var row = locals[cdt][cdn];
        // let custom_cost = row.custom_avg_rate * row.qty;
        // frappe.model.set_value(cdt, cdn, 'custom_cost', custom_cost);
    // },
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
    // custom_average_rate(frm, cdt, cdn) {
    //     var row = locals[cdt][cdn];
    //     if (row.custom_average_rate>0){
    //         let custom_cost1 = row.custom_average_rate * row.qty;
    //         frappe.model.set_value(cdt, cdn, 'custom_item_cost', custom_cost1);
    //     }
    // },
 });