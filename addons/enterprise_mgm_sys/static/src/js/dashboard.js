odoo.define('enterprise_mgm_sys_dashboard.dashboard', function (require) {
    "use strict";
    var framework = require('web.framework');
    var core = require('web.core');
    var formats = require('web.formats');
    var Model = require('web.Model');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var KanbanView = require('web_kanban.KanbanView');
    var KanbanRecord = require('web_kanban.Record');
    var ActionManager = require('web.ActionManager');
    var crash_manager = require('web.crash_manager');
    var utils = require('web.utils');
    var QWeb = core.qweb;

    var _t = core._t;
    var _lt = core._lt;

    var EnterpriseMgmSysView = KanbanView.extend({
        display_name: _lt('Dashboard'),
        icon: 'fa-dashboard text-red',
        searchview_hidden: true,//  To hide the search and filter bar
        events: {
            'click .enterprise_mgm_sys_process_file': 'action_process_file',
            'click .enterprise_mgm_sys_process_evaluations': 'action_process_evaluations',
            'click .enterprise_mgm_sys_docs_action': 'docs_action',
            'click .enterprise_mgm_sys_agreement_action': 'agreement_action',
            'click .enterprise_mgm_sys_no_conf_action': 'no_conformity_action',
            'click .enterprise_mgm_sys_audit_action': 'audits_action',
        },
        init: function (parent, dataset, view_id, options) {
            this._super(parent, dataset, view_id, options);
            var self = this;
            this.ViewManager.on("switch_mode", self, function (n_mode) {
                if (self.ViewManager.active_view.type === 'enterprise_mgm_sys_dashboard_view') {
                    self.ViewManager.update_control_panel({hidden: true})
                }
            });
            this.options.creatable = false;
        },
        fetch_data: function () {
            // Overwrite this function with useful data
            return $.when();
        },
        // Here we are calling a function 'get_employee_info' from model to retrieve enough data
        render: function () {
            var super_render = this._super;
            var self = this;
            var model = new Model('enterprise_mgm_sys.dashboard').call('get_data_info').then(function (result) {
                self.isFirefox = typeof InstallTrigger !== 'undefined';
                self.enterprise_mgm_sys_data = result
                return self.fetch_data().then(function (result) {
                    var dashboard = QWeb.render('enterprise_mgm_sys_dashboard.dashboard', {
                        widget: self,
                    });
                    super_render.call(self);
                    $(dashboard).prependTo(self.$el);
                })
            });
        },

        action_process_file: function (ev) {
            var self = this;
            ev.stopPropagation();
            ev.preventDefault();
            var value = $(ev.currentTarget).attr('data-process_file_id');
            if (value) {
                framework.blockUI();
                var c = crash_manager;
                this.session.get_file({
                    'url': '/web/content',
                    'data': {
                        'model': 'enterprise_mgm_sys.registry_line',
                        'id': value,
                        'field': 'file',
                        'filename_field': 'name',
                        'filename': "",
                        'download': true,
                        'data': utils.is_bin_size(value) ? null : value,
                    },
                    'complete': framework.unblockUI,
                    'error': c.rpc_error.bind(c)
                });
                ev.stopPropagation();
            }
        },

        action_process_evaluations: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            var id = $(event.currentTarget).attr('data-process_id');
            if (id) {
                this.do_action({
                    name: _t("Evaluations"),
                    type: 'ir.actions.act_window',
                    res_model: 'enterprise_mgm_sys.process_efficacy',
                    view_mode: 'tree,form,graph,pivot',
                    view_type: 'form',
                    views: [[false, 'list'], [false, 'form'], [false, 'graph'], [false, 'pivot']],
                    domain: [['process_id', '=', parseInt(id, 10)]],
                    target: 'current',
                    context: {
                        search_default_process_x_month: true,
                        search_default_this_year: true
                    }
                })
            }
        },

        docs_action: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action('enterprise_mgm_sys.enterprise_mgm_sys_registry_act_window')
        },

        agreement_action: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action('enterprise_mgm_sys.enterprise_mgm_sys_internal_agreement_act_window')
        },

        audits_action: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action('enterprise_mgm_sys.enterprise_mgm_sys_audit_action')
        },

        no_conformity_action: function (event) {
            var self = this;
            event.stopPropagation();
            event.preventDefault();
            this.do_action('enterprise_mgm_sys.enterprise_mgm_sys_no_conformity_action')
        },


        // Function which gives random color for charts.
        getRandomColor: function () {
            var letters = '0123456789ABCDEF'.split('');
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            return color;
        },

    });
// View adding to the registry
    core.view_registry.add('enterprise_mgm_sys_dashboard_view', EnterpriseMgmSysView);
    return EnterpriseMgmSysView;
});
