frappe.ui.form.on('Sales Invoice Item', {
    rate(frm, cdt, cdn) {
        var row = locals[cdt][cdn];
        let or_amount = row.rate * row.original_qty;
        frappe.model.set_value(cdt, cdn, 'original_amount', or_amount);
    },
 });