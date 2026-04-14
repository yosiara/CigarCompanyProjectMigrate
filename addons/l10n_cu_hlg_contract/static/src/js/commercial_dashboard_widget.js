odoo.define('dashboard_commercial', function (require) {
    'use strict';

    var kanban_widgets = require('web_kanban.widgets');

    var CommercialDashboardGraph = kanban_widgets.AbstractField.extend({


        start: function () {
            this.graph_type = this.$node.attr('graph_type');
            this.test = this.$node.attr('test');
            this.data = JSON.parse(this.field.raw_value);
            this.display_graph();
            return this._super();
        },

        display_graph: function () {
            var self = this;
            nv.addGraph(function () {
                self.$svg = self.$el.append('<svg>');

                switch (self.graph_type) {

                    case "bar":
                        self.$svg.addClass('o_graph_barchart');

                        self.chart = nv.models.discreteBarChart()
                            .x(function (d) {
                                return d.label
                            })
                            .y(function (d) {
                                return d.value
                            })
                            .showValues(false)
                            .showYAxis(false)
                            .margin({'left': 0, 'right': 0, 'top': 0, 'bottom': 40});

                        self.chart.xAxis.axisLabel(self.data[0].title);
                        self.chart.yAxis.tickFormat(d3.format(',.0f'));
                        self.chart.yAxis.tickSize(20)

                        break;
                }
                d3.select(self.$el.find('svg')[0])
                    .datum(self.data)
                    .transition().duration(1200)
                    .call(self.chart);

                self.customize_chart();

                nv.utils.windowResize(self.on_resize);

                // d3.selectAll(".nv-bar").on('click', self.click_example);
                d3.selectAll(".nv-bar").on('click', function () {
                    // alert(this.__data__.start_date);
                    var additional_context = {};
                    var domain = {};
                    var action_name = '';

                    self.do_action({
                        res_model: 'l10n_cu_contract.contract',
                        name: ('Contract'),
                        domain: [['date_end', '>=', this.__data__.start_date],['date_end', '<=', this.__data__.last_date],
                                ['flow', '=', this.__data__.flow]],
                        views: [[false, 'list'], [false, 'form']],
                        type: 'ir.actions.act_window',
                        view_type: 'list',
                        view_mode: 'list',
                        target: 'current',
                    })
                });
            });
        },

        on_resize: function () {
            this.chart.update();
            this.customize_chart();
        },

        customize_chart: function () {
            if (this.graph_type === 'bar') {
                // Add classes related to time on each bar of the bar chart
                var bar_classes = _.map(this.data[0].values, function (v, k) {
                    return v.type
                });

                _.each(this.$('.nv-bar'), function (v, k) {
                    // classList doesn't work with phantomJS & addClass doesn't work with a SVG element
                    $(v).attr('class', $(v).attr('class') + ' ' + bar_classes[k]);

                });
            }
        },

        destroy: function () {
            nv.utils.offWindowResize(this.on_resize);
            this._super();
        },

    });


    kanban_widgets.registry.add('commercial_dashboard_graph', CommercialDashboardGraph);

});