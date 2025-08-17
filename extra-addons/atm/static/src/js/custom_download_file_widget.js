/* custom_download_file_widget.js
 * ==============================
 * Widget to download any document from a form...
 *
 * @Author  Alejandro Cora González
 * @Email   alek.cora.glez@gmail.com
 * @version 1.0.0
 */

odoo.define('download_file_widget', function (require) {"use strict"; var core = require('web.core'); var form_common = require('web.form_common'); var framework = require('web.framework'); var CrashManager = require('web.CrashManager'); var WidgetDownloadFile = form_common.FormWidget.extend({template: 'WidgetDownloadFile', events: {'click': function () {var self = this; var crash_manager = new CrashManager(); self.view.save().then(function () {framework.blockUI(); self.session.get_file({url: '/custom_download_file/', data: {data: JSON.stringify({model: self.node.attrs['model'], record_id: self.view.datarecord.id }) }, complete: framework.unblockUI, error: crash_manager.rpc_error.bind(crash_manager) }); }); } }, init: function() {this._super.apply(this, arguments); } }); core.form_custom_registry.add('download_file', WidgetDownloadFile); });
