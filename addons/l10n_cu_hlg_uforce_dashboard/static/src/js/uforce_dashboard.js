odoo.define('l10n_cu_hlg_uforce_dashboard.dashboard', function (require) {
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

var UforceView = KanbanView.extend({
    display_name: _lt('Dashboard'),
    icon: 'fa-dashboard text-red',
    searchview_hidden: true,//  To hide the search and filter bar
    events: {
        'click .dashboard-uforce': 'action_uforce',
        'click .uforce_count_six_grade': 'action_count_six_grade',
        'click .uforce_count_nine_grade': 'action_count_nine_grade',
        'click .uforce_count_twelve_grade': 'action_count_twelve_grade',
        'click .uforce_count_tecnical_grade': 'action_count_tecnical_grade',
        'click .uforce_count_university_grade': 'action_count_university_grade',
        'click .uforce_count_six_grade_female': 'action_count_six_grade_female',
        'click .uforce_count_nine_grade_female': 'action_count_nine_grade_female',
        'click .uforce_count_twelve_grade_female': 'action_count_twelve_grade_female',
        'click .uforce_count_tecnical_grade_female': 'action_count_tecnical_grade_female',
        'click .uforce_count_university_grade_female': 'action_count_university_grade_female',
        'click .uforce_count_six_grade_male': 'action_count_six_grade_male',
        'click .uforce_count_nine_grade_male': 'action_count_nine_grade_male',
        'click .uforce_count_twelve_grade_male': 'action_count_twelve_grade_male',
        'click .uforce_count_tecnical_grade_male': 'action_count_tecnical_grade_male',
        'click .uforce_count_university_grade_male': 'action_count_university_grade_male',
        'click .uforce_age_range_one_count': 'action_age_range_one_count',
        'click .uforce_age_range_two_count': 'action_age_range_two_count',
        'click .uforce_age_range_three_count': 'action_age_range_three_count',
        'click .uforce_age_range_four_count': 'action_age_range_four_count',
        'click .uforce_age_range_one_count_female': 'action_age_range_one_count_female',
        'click .uforce_age_range_two_count_female': 'action_age_range_two_count_female',
        'click .uforce_age_range_three_count_female': 'action_age_range_three_count_female',
        'click .uforce_age_range_four_count_female': 'action_age_range_four_count_female',
        'click .uforce_age_range_one_count_male': 'action_age_range_one_count_male',
        'click .uforce_age_range_two_count_male': 'action_age_range_two_count_male',
        'click .uforce_age_range_three_count_male': 'action_age_range_three_count_male',
        'click .uforce_age_range_four_count_male': 'action_age_range_four_count_male',
        'click #generate_chart_count_categ_pdf': function(){this.generate_chart_categ_pdf();},
//        'click .my_profile': 'action_my_profile',
    },
    init: function (parent, dataset, view_id, options) {
        this._super(parent, dataset, view_id, options);
        this.options.creatable = false;
        var uid = dataset.context.uid;
        var uforce_data = true;
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
        var model  = new Model('l10n_cu_hlg_uforce_dashboard.dashboard').call('get_data_info').then(function(result){
            self.isFirefox = typeof InstallTrigger !== 'undefined';
            self.uforce_data =  result[0]
            return self.fetch_data().then(function(result){
                var uforce_dashboard = QWeb.render('l10n_cu_hlg_uforce_dashboard.dashboard', {
                    widget: self,
                });
                super_render.call(self);
                $(uforce_dashboard).prependTo(self.$el);
                self.graph();
            })
        });
    },

    action_uforce: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return this.do_action({
            name: _t("UForce"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            view_id: self.uforce_data['view_uforce_id']
        })
    },

     action_count_six_grade: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Six grade list"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','6to grado']],

        })
    },

    action_count_nine_grade: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Nine grade list"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','9no grado']],

        })
    },

     action_count_twelve_grade: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Twelve grade list"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','12mo grado']],

        })
    },

    action_count_tecnical_grade: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Tecnical list"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Técnico Medio']],

        })
    },

    action_count_university_grade: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("University list"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Universitario']],

        })
    },

    action_count_six_grade_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Six Grade List Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','6to grado'],['gender','=','female']],

        })
    },

    action_count_nine_grade_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Nine Grade List Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','9no grado'],['gender','=','female']],

        })
    },

    action_count_twelve_grade_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Twelve Grade List Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','12mo grado'],['gender','=','female']],

        })
    },

    action_count_tecnical_grade_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Tecnical Grade List Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Técnico Medio'],['gender','=','female']],

        })
    },

    action_count_university_grade_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("University Grade List Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Universitario'],['gender','=','female']],

        })
    },

    action_count_six_grade_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Six Grade List Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','6to grado'],['gender','=','male']],

        })
    },

    action_count_nine_grade_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Nine List Grade Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','9no grado'],['gender','=','male']],

        })
    },

    action_count_twelve_grade_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Twelve List Grade Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','12mo grado'],['gender','=','male']],

        })
    },

    action_count_tecnical_grade_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Tecnical Grade List Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Técnico Medio'],['gender','=','male']],

        })
    },

    action_count_university_grade_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("University Grade List Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['school_level_name','=','Universitario'],['gender','=','male']],

        })
    },

    action_age_range_one_count: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List Under 31"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2920']],

        })
    },

    action_age_range_two_count: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 31 to 50"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2921']],

        })
    },

    action_age_range_three_count: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 51 to 60"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2922']],

        })
    },

    action_age_range_four_count: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List More 60"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2923']],

        })
    },

    action_age_range_one_count_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List Under 31 Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2920'],['gender','=','female']],

        })
    },

      action_age_range_two_count_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 31 to 50 Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2921'],['gender','=','female']],

        })
    },
      action_age_range_three_count_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 51 to 60"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2922'],['gender','=','female']],

        })
    },

      action_age_range_four_count_female: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List More 60 Female"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2923'],['gender','=','female']],

        })
    },

      action_age_range_one_count_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List Under 31 Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2920'],['gender','=','male']],

        })
    },

       action_age_range_two_count_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 31 to 50 Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2921'],['gender','=','male']],

        })
    },

       action_age_range_three_count_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List 51 to 60 Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2922'],['gender','=','male']],

        })
    },

       action_age_range_four_count_male: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("List More 60 Male"),
            type: 'ir.actions.act_window',
            res_model: 'hr.employee',
            view_mode: 'tree,form',
            view_type: 'form',
            views: [[false, 'list'],[false, 'form']],
            target: 'current',
            domain:[['age_range_code','=','2923'],['gender','=','male']],

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
        /*var myChart = new Chart(ctx, {
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
        });*/

        var piectx = this.$el.find('#myChartOcuppationalCategory');
        bg_color_list = []
        for (var i=0;i<=self.uforce_data['categ_ocup_list'].length;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChart = new Chart(piectx, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.uforce_data['categ_ocup_list'],
//                    backgroundColor: bg_color_list,
//                    backgroundColor: ['#f3eae0', '#f4bc74', '#f4ac54', '#f4a242', '#965e1e', '#cea16d',
//                                      '#d4b49c', '#f4942c', '#cc8424', '#e48c2c', '#f49c2c', '#b48c5c'],
                    backgroundColor: ['#f3eae0','#FBF6CB', '#ABA043', '#FBB93A','#f4bc74', '#F08C12', '#94642C', '#CC6E02','#FBC485','#F9E3C9'],
                    label: 'Categorys Occupational'
                }],
                labels: self.uforce_data['categs_labels'],
            },
            options: {
                responsive: true
            }
        });

        var piectxTFD = this.$el.find('#myChartTopFiveDegree');
        bg_color_list = []
        for (var i=0;i<5;i++){
            bg_color_list.push(self.getRandomColor())
        }
        var pieChartTFD = new Chart(piectxTFD, {
            type: 'pie',
            data: {
                datasets: [{
                    data: self.uforce_data['top_five_list'],
//                    backgroundColor: bg_color_list,
//                    backgroundColor: ['#f3eae0', '#f4bc74', '#f4ac54', '#f4a242', '#965e1e', '#cea16d',
//                                      '#d4b49c', '#f4942c', '#cc8424', '#e48c2c', '#f49c2c', '#b48c5c'],
                    backgroundColor: ['#3DC1F8', '#0C516E', '#D0EDF9', '#0FFBF3', '#D0DBFA'],
                    label: 'Top Five List'
                }],
                labels: self.uforce_data['top_five_labels'],
            },
            options: {
                responsive: true
            }
        });


    },

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
core.view_registry.add('uforce_dashboard_view', UforceView);
return UforceView;
});
