odoo.define('turei_retired_person_dashboard.dashboard', function (require) {
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

var RetiredView = KanbanView.extend({
    display_name: _lt('Tablero'),
    icon: 'fa-dashboard text-red',
    searchview_hidden: true,//  To hide the search and filter bar
    events: {
        'click .dashboard-retired': 'action_retired',
        'click .retired_count_ist': 'action_count_ist',
        'click .retired_count_pc': 'action_count_pc',
        'click .retired_count_spi': 'action_count_spi',
        'click .retired_count_ca': 'action_count_ca',
        'click .retired_count_sg': 'action_count_sg',
        'click .retired_count_dcf': 'action_count_dcf',
        'click .retired_count_dch': 'action_count_dch',
        'click .retired_count_dtd': 'action_count_dtd',
        'click .retired_count_pad': 'action_count_pad',
        'click .retired_count_de': 'action_count_de',
        'click .retired_count_founder': 'action_count_founder',
        'click .retired_count_other': 'action_count_other',
        'click .retired_count_dead': 'action_count_dead',
        'click .retired_count_founder_female': 'action_count_founder_female',
        'click .retired_count_other_female': 'action_count_other_female',
        'click .retired_count_dead_female': 'action_count_dead_female',
        'click .retired_count_founder_male': 'action_count_founder_male',
        'click .retired_count_other_male': 'action_count_other_male',
        'click .retired_count_dead_male': 'action_count_dead_male',


        'click #generate_chart_count_categ_pdf': function(){this.generate_chart_categ_pdf();},
//        'click .my_profile': 'action_my_profile',
    },
    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        this.options.creatable = false;
        var uid = dataset.context.uid;
        var retired_data = true;
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
        var model  = new Model('turei_retired_person_dashboard.dashboard').call('get_data_info').then(function(result){
            self.isFirefox = typeof InstallTrigger !== 'undefined';
            self.retired_data =  result[0]
            return self.fetch_data().then(function(result){
                var retired_dashboard = QWeb.render('turei_retired_person_dashboard.dashboard', {
                    widget: self,
                });
                super_render.call(self);
                $(retired_dashboard).prependTo(self.$el);
                //self.graph();
            })
        });
    },

    action_retired: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("Jubilados"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            view_id: self.retired_data['view_retired_id']
        })
    },

     action_count_ist: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en IST"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','IST']],

        })
    },

    action_count_pc: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en PC"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','PC']],

        })
    },

     action_count_spi: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en SPI"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','SPI']],

        })
    },

    action_count_ca: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en CA"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','CA']],

        })
    },

    action_count_sg: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en SG"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','SG']],

        })
    },

    action_count_dcf: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en DCF"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','DCF']],

        })
    },

    action_count_dch: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en DCH"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','DCH']],

        })
    },

    action_count_dtd: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en DTD"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','DTD']],

        })
    },

    action_count_pad: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en PAD"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','PAD']],

        })
    },

    action_count_de: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en DE"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['ueb_id.code','=','DE']],

        })
    },

    action_count_founder: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Fundadores"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['founder','=','True']],

        })
    },



    action_count_other: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Jubilados en Otra Entidad"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['retired_in_turei_str','=','NT']],

        })
    },

    action_count_dead: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Fallecidos"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['dead_person','=','True']],

        })
    },

     action_count_founder_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Hombres Fundadores"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['founder','=','True'],['gender','=','Male']],

        })
    },


    action_count_other_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Hombres Jubilados en Otra Entidad"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['retired_in_turei_str','=','NT'],['gender','=','Male']],

        })
    },

    action_count_dead_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Hombres Fallecidos"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['dead_person','=','True'],['gender','=','Male']],

        })
    },

    action_count_founder_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Mujeres Fundadoras"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['founder','=','True'],['gender','=','Female']],

        })
    },


    action_count_other_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Mujeres Jubiladas en Otra Entidad"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['retired_in_turei_str','=','NT'],['gender','=','Female']],

        })
    },

    action_count_dead_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Mujeres Fallecidas"),
            type: 'ir.actions.act_window',
            res_model: 'turei_retired_person.retired_person',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['dead_person','=','True'],['gender','=','Female']],

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
//    graph: function() {
//        var self = this
//        var ctx = this.$el.find('#myChartProductionMonth')
//        // Fills the canvas with white background
//        Chart.plugins.register({
//          beforeDraw: function(chartInstance) {
//            var ctx = chartInstance.chart.ctx;
//            ctx.fillStyle = "white";
//            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
//          }
//        });
//        var bg_color_list = []
//        for (var i=0;i<=12;i++){
//            bg_color_list.push(self.getRandomColor())
//        }
//        /*var myChart = new Chart(ctx, {
//            type: 'bar',
//            data: {
//                labels: self.sale_contract_data['invoices_labels'],
//                datasets: [{
//                    label: '$',
//                    data: self.sale_contract_data['invoices_total_by_month'],
//                    backgroundColor: '#f49c2c',
//                    borderColor: '#f49c2c',
////                    backgroundColor: bg_color_list,
////                    borderColor:bg_color_list,
//                    borderWidth: 1,
//                    pointBorderColor: 'white',
//                    pointBackgroundColor: 'red',
//                    pointRadius: 5,
//                    pointHoverRadius: 10,
//                    pointHitRadius: 30,
//                    pointBorderWidth: 2,
//                    pointStyle: 'rectRounded'
//                }]
//            },
//            options: {
//                scales: {
//                    yAxes: [{
//                        ticks: {
//                            min: 0,
//                            max: Math.max.apply(null,self.sale_contract_data['invoices_total_by_month']),
//                            stepSize: self.sale_contract_data['invoices_total_by_month'].reduce((pv,cv)=>{return pv + (parseFloat(cv)||0)},0)
//                            /self.sale_contract_data['invoices_total_by_month'].length
//                          }
//                    }]
//                },
//                responsive: true,
//                maintainAspectRatio: true,
//                animation: {
//                    duration: 100, // general animation time
//                },
//                hover: {
//                    animationDuration: 500, // duration of animations when hovering an item
//                },
//                responsiveAnimationDuration: 500, // animation duration after a resize
//                legend: {
//                    display: true,
//                    labels: {
//                        fontColor: '#f49c2c'
//                    }
//                },
//            },
//        });*/
//
//        var piectx = this.$el.find('#myChartOcuppationalCategory');
//        bg_color_list = []
//        for (var i=0;i<=self.uforce_data['categ_ocup_list'].length;i++){
//            bg_color_list.push(self.getRandomColor())
//        }
//        var pieChart = new Chart(piectx, {
//            type: 'pie',
//            data: {
//                datasets: [{
//                    data: self.uforce_data['categ_ocup_list'],
////                    backgroundColor: bg_color_list,
////                    backgroundColor: ['#f3eae0', '#f4bc74', '#f4ac54', '#f4a242', '#965e1e', '#cea16d',
////                                      '#d4b49c', '#f4942c', '#cc8424', '#e48c2c', '#f49c2c', '#b48c5c'],
//                    backgroundColor: ['#f3eae0','#FBF6CB', '#ABA043', '#FBB93A','#f4bc74', '#F08C12', '#94642C', '#CC6E02','#FBC485','#F9E3C9'],
//                    label: 'Categorys Occupational'
//                }],
//                labels: self.uforce_data['categs_labels'],
//            },
//            options: {
//                responsive: true
//            }
//        });
//
//        var piectxTFD = this.$el.find('#myChartTopFiveDegree');
//        bg_color_list = []
//        for (var i=0;i<5;i++){
//            bg_color_list.push(self.getRandomColor())
//        }
//        var pieChartTFD = new Chart(piectxTFD, {
//            type: 'pie',
//            data: {
//                datasets: [{
//                    data: self.uforce_data['top_five_list'],
////                    backgroundColor: bg_color_list,
////                    backgroundColor: ['#f3eae0', '#f4bc74', '#f4ac54', '#f4a242', '#965e1e', '#cea16d',
////                                      '#d4b49c', '#f4942c', '#cc8424', '#e48c2c', '#f49c2c', '#b48c5c'],
//                    backgroundColor: ['#3DC1F8', '#0C516E', '#D0EDF9', '#0FFBF3', '#D0DBFA'],
//                    label: 'Top Five List'
//                }],
//                labels: self.uforce_data['top_five_labels'],
//            },
//            options: {
//                responsive: true
//            }
//        });
//
//
//    },

    generate_chart_categ_pdf: function(chart){
        var canvas = document.querySelector('#myChartOcuppationalCategory');

        //creates image
        var canvasImg = canvas.toDataURL("image/jpeg", 1.0);
        var doc = new jsPDF('landscape');
        doc.setFontSize(20);
        doc.addImage(canvasImg, 'JPEG', 10, 10, 280, 150 );
        doc.save('report.pdf');
    },

})
// View adding to the registry
core.view_registry.add('retired_dashboard_view', RetiredView);
return RetiredView;
});
