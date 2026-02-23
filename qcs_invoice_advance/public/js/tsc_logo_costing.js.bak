frappe.ui.form.on('TSC Logo Costing', {
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
            let phoneNumber = '971556983424';  // Replace with the actual phone number

            // Fetching the customer name
            let customerName = frm.doc.customer_name || 'Customer';

            // Custom message
            let customMessage = `Please can you let us know the price for this logo for ${customerName}. Thanks. `;
            let message = customMessage + costing_links.join(', ');

            // Generate WhatsApp web link
            let whatsappLink = `https://wa.me/${phoneNumber}?text=${encodeURIComponent(message)}`;

            // Open WhatsApp web link in a new tab/window
            window.open(whatsappLink, '_blank');
        } else {
            frappe.msgprint(__('No costing links found.'));
        }
    }
});

frappe.ui.form.on('TSC Logo Details', {
    custom_copy_link: function(frm, cdt, cdn) {
        // Get the specific row being acted upon
        let row = locals[cdt][cdn];

        if (row.costing_link) {
            // Use the modern Clipboard API to copy the link
            navigator.clipboard.writeText(row.costing_link)
                .then(() => {
                    frappe.show_alert({message: 'Link copied to clipboard!', indicator: 'green'});
                })
                .catch(err => {
                    console.error('Error copying to clipboard:', err);
                    frappe.msgprint(__('Failed to copy link to clipboard.'));
                });
        }
    }
});