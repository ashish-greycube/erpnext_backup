// Copyright (c) 2018, GreyCube Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on('Backup Settings', {
	refresh: function (frm) {

	},
	onload_post_render: function () {
		cur_frm.fields_dict.manual_backup.$input.addClass("btn-primary");
	},
	validate_send_notifications_to: function () {
		if (!cur_frm.doc.send_notifications_to) {
			msgprint(__("Please specify") + ": " +
				__(frappe.meta.get_label(cur_frm.doctype,
					"send_notifications_to")));
			return false;
		}
		return true;
	},
	manual_backup: function (frm) {
		if (frm.doc.enable_backup) {
			frappe.msgprint(__("Performing Backup"));
			frappe.call({
				method: "erpnext_backup.erpnext_backup.doctype.backup_settings.backup_settings.take_backup",
				freeze: false,
				callback: function (r) {
					frappe.errprint(r)
				}
			})
		} else {
			frappe.msgprint(__("Backup is not enabled"));
		}
	}
});