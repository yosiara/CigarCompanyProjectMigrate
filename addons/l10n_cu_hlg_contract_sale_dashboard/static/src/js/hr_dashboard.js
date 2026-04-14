odoo.define('l10n_cu_hlg_contract_sale_dashboard.dashboard', function (require) {
"use strict";
var core = require('web.core');
var formats = require('web.formats');
var Model = require('web.Model');
var session = require('web.session');
var ajax = require('web.ajax');
var KanbanView = require('web_kanban.KanbanView');
var KanbanRecord = require('web_kanban.Record');
var ActionManager = require('web.ActionManager');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;

var ContractSaleView = KanbanView.extend({
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard text-red',
    searchview_hidden: true,//  To hide the search and filter bar
    events: {
        'click .dashboard-invoice': 'action_invoice',
        'click .contract': 'action_contract',
        'click .contract_count_draft': 'action_contract_draft',
        'click .contract_count_pending_dict': 'action_contract_count_pending_dict',
        'click .contract_count_pending_appro': 'action_contract_count_pending_appro',
        'click .contract_count_approval': 'action_contract_count_approval',
        'click .contract_count_pending_signed': 'action_contract_count_pending_signed',
        'click .contract_count_open': 'action_contract_count_open',
        'click .contract_count_close': 'action_contract_count_close',
        'click .invoice_count_draft': 'action_invoice_count_draft',
        'click .invoice_count_open': 'action_invoice_count_open',
        'click .invoice_count_paid': 'action_invoice_count_paid',
        'click .invoice_count_cancelled': 'action_invoice_count_cancelled',
        'click #generate_chart_pdf': function(){this.generate_chart_pdf("bar");},
        'click #generate_chart_count_pdf': function(){this.generate_chart_pdf("pie");},
//        'click .my_profile': 'action_my_profile',
    },
    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        this.options.creatable = false;
        var uid = dataset.context.uid;
        var sale_contract_data = true;
        var isFirefox = false;
        //Here we can bind any functions to be called before or after render.
        //_.bindAll(this, 'render', 'graph');
        //var _this = this;
        //this.render = _.wrap(this.render, function(render) {
        //    render();
        //    _this.graph();
        //    return _this;
        //});
    },
    fetch_data: function() {
		// Overwrite this function with useful data
		return $.when();
	},
	// Here we are calling a function 'get_employee_info' from model to retrieve enough data
    render: function() {
        var super_render = this._super;
        var self = this;
        var model  = new Model('contract.sale.dashboard').call('get_data_info').then(function(result){
            self.isFirefox = typeof InstallTrigger !== 'undefined';
            self.sale_contract_data =  result[0]
            return self.fetch_data().then(function(result){
                var hr_dashboard = QWeb.render('l10n_cu_hlg_contract_sale_dashboard.dashboard', {
                    widget: self,
                });
                super_render.call(self);
                $(hr_dashboard).prependTo(self.$el);
                self.graph();
            })
        });
    },

    action_contract: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain:[['flow','=','customer'],['state','=', 'open'],['parent_id', '=', false]],
            target: 'current',

        })
    },
    action_contract_draft: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','draft'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_pending_dict: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','pending_dict'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_pending_appro: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','pending_appro'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_approval: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','approval'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_pending_signed: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','pending_signed'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_open: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','open'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_close: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','close'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_contract_count_cancelled: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Sales Contracts"),
            type: 'ir.actions.act_window',
            res_model: 'l10n_cu_contract.contract',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['state','=','cancelled'],['flow','=','customer'],['parent_id', '=', false]],

        })
    },
    action_invoice: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Sales Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','in',['out_invoice']]],
            target: 'current',
            view_id: self.sale_contract_data['view_invoice_id']
        })
    },
    action_invoice_count_draft: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Sales Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','in',['out_invoice']], ['state','=','draft']],
            target: 'current',
            view_id: self.sale_contract_data['view_invoice_id']
        })
    },
    action_invoice_count_open: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Sales Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','in',['out_invoice']], ['state','=','open']],
            target: 'current',
            view_id: self.sale_contract_data['view_invoice_id']
        })
    },
    action_invoice_count_paid: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Sales Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','in',['out_invoice']], ['state','=','paid']],
            target: 'current',
            view_id: self.sale_contract_data['view_invoice_id']
        })
    },
    action_invoice_count_cancelled: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Sales Invoices"),
            type: 'ir.actions.act_window',
            res_model: 'account.invoice',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            domain: [['type','in',['out_invoice']], ['state','=','cancelled']],
            target: 'current',
            view_id: self.sale_contract_data['view_invoice_id']
        })
    },
    // Function which gives random color for charts.
    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    // Here we are plotting bar,pie chart
    graph: function() {
        var self = this
        var ctx = this.$el.find('#myChartProductionMonth')
        // Fills the canvas with white background
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: self.sale_contract_data['invoices_labels'],
                datasets: [{
                    label: '$',
                    data: self.sale_contract_data['invoices_total_by_month'],
                    backgroundColor: '#f49c2c',
                    borderColor: '#f49c2c',
//                    backgroundColor: bg_color_list,
//                    borderColor:bg_color_list,
                    borderWidth: 1,
                    pointBorderColor: 'white',
                    pointBackgroundColor: 'red',
                    pointRadius: 5,
                    pointHoverRadius: 10,
                    pointHitRadius: 30,
                    pointBorderWidth: 2,
                    pointStyle: 'rectRounded'
                }]
            },
            options: {
                scales: {
                    yAxes: [{
                        ticks: {
                            min: 0,
                            max: Math.max.apply(null,self.sale_contract_data['invoices_total_by_month']),
                            stepSize: self.sale_contract_data['invoices_total_by_month'].reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
                            /self.sale_contract_data['invoices_total_by_month'].length
                          }
                    }]
                },
                responsive: true,
                maintainAspectRatio: true,
                animation: {
                    duration: 100, // general animation time
                },
                hover: {
                    animationDuration: 500, // duration of animations when hovering an item
                },
                responsiveAnimationDuration: 500, // animation duration after a resize
                legend: {
                    display: true,
                    labels: {
                        fontColor: '#f49c2c'
                    }
                },
            },
        });

        var piectx = this.$el.find('#myChartInvoiceMonth');
        bg_color_list = []
        for (var i=0;i<=self.sale_contract_data['invoices_by_month'].length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.sale_contract_data['invoices_by_month'],
//                    backgroundColor: bg_color_list,
                    backgroundColor: ['#f3eae0', '#f4bc74', '#f4ac54', '#f4a242', '#965e1e', '#cea16d',
                                      '#d4b49c', '#f4942c', '#cc8424', '#e48c2c', '#f49c2c', '#b48c5c'],
                    label: 'Cantidad de Facturas'
                }],
                labels: self.sale_contract_data['invoices_labels'],
            },
            options: {
                responsive: true
            }
        });

    },
    generate_chart_pdf: function(chart){
        if (chart == 'bar'){
            var canvas = document.querySelector('#myChartProductionMonth');
        }
        else if (chart == 'pie') {
            var canvas = document.querySelector('#myChartInvoiceMonth');
        }

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    },
})
// View adding to the registry
core.view_registry.add('sale_contract_dashboard_view', ContractSaleView);
return ContractSaleView;
});
