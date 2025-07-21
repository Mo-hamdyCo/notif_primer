frappe.ui.form.on('Notification Mange', {
    target_doctype: function(frm) {
        if (!frm.doc.target_doctype) return;

        frappe.model.with_doctype(frm.doc.target_doctype, function () {
            const fields = frappe.get_doc("DocType", frm.doc.target_doctype).fields;

            const get_select_options = function(df) {
                return {
                    label: `${df.label} (${df.fieldname})`,
                    value: df.fieldname
                };
            };

            const date_options = fields
                .filter(df => df.fieldtype === "Date" || df.fieldtype === "Datetime")
                .map(get_select_options);

            // إضافة الحقول الأساسية اللي Frappe بتستخدمها دايمًا
            date_options.push(
                { value: "creation", label: `Created On (creation)` },
                { value: "modified", label: `Last Modified (modified)` }
            );

            // ضبط خيارات حقل target_date_field
            frm.set_df_property("target_date_field", "options", [""].concat(date_options.map(d => d.value)));
            frm.refresh_field("target_date_field");

            // إعادة تعيين القيمة
            frm.set_value("target_date_field", "");
        });
    }
});
