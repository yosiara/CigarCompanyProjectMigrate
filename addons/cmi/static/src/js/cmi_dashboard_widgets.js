odoo.define('cmi_dashboard', function (require) {
    'use strict';

    var core = require("web.core");
    var form_common = require('web.form_common');
    var config = require('web.config');
    var utils = require('web.utils');
    var data = require('web.data');
    var _t = core._t;

    // hide top legend when too many item for device size
    var MAX_LEGEND_LENGTH = 25 * (1 + config.device.size_class);

    var CMIDashboardWidget = form_common.AbstractField.extend({
        template: 'CmiDashboardContainer',
        className: '',
        init: function (field_manager, node) {
            this._super(field_manager, node);
            var self = this;
            this.view.ViewManager.on("switch_mode", self, function(n_mode) {
                if(self.view.ViewManager.active_view.type === 'form'){
                    self.view.ViewManager.update_control_panel({hidden: true})
                }
            });
        },
        render_value: function () {
            this.data = JSON.parse(this.get('value'));
            this.displayDashboard();
        },
        displayDashboard: function () {
            if (this.charts) {
                for (var i = 0; i < this.charts.length; i++) {
                    nv.utils.offWindowResize(this.charts[i].update);
                }
            }
            this.charts = [];
            this.$el.empty();
            var self = this;
            this.$el.removeClass('o_form_field');
            for (var i = 0; i < self.data.length; i++) {
                this.displayChart(this.data[i], this.$el);
            }
        },
        displayChart: function (data, $el) {
            var self = this;
            nv.addGraph(function () {
                self.$el.append('<div class="text-center col-xs-12 col-md-6"><h5 class="o_primary"><b>' + data.indicator + '</b></h5><div id="'+data.indicator_id+'" class="o_graph_svg_container"></div></div>');
                var container = $el.find('#' + data.indicator_id);
                var chart_type = data.chart_type;
                var svg = d3.select(container[0]).append('svg');
                svg.datum(data.data);
                svg.transition().duration(1200);
                var chart;
                switch (chart_type) {
                    case "pie":
                        chart = nv.models.pieChart();
                        chart.options({
                            delay: 250,
                            noData: _t("No Data Available."),
                            showLegend: true,
                            showLabels: true,
                            legendPosition: 'top',
                            transition: 100,
                            labelType: 'percent',
                            color: d3.scale.category10().range(),
                        });
                        chart.x(function (d) {
                            return d.label
                        })
                            .y(function (d) {
                                return d.value
                            });
                        // chart.xAxis.axisLabel(data.indicator);
                        break;
                    case "line":
                        chart = nv.models.lineChart();
                        chart.options({
                            showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                            noData: _t("No Data Available."),
                            showXAxis: true,
                            showYAxis: true,
                            color: d3.scale.category10().range(),
                        });
                        chart.x(function (d) {
                            return d.key;
                        })
                        .y(function (d) {
                            return d.value
                        })
                        .margin({
                            top: 30,
                            right: 20,
                            bottom: 50,
                            left: 85
                        });
                        chart.xAxis
                            .tickFormat(function (d) {
                            return data.ticks[d];
                            })
                            .tickValues(data.ticks.keys)
                            .rotateLabels(-20);
                        chart.yAxis.tickFormat(d3.format(',.02f'));
                        chart.yAxis.tickSize(20);
                        break;
                    default:
                        chart = nv.models.multiBarChart();
                        chart.options({
                            // margin: {left: 120, bottom: 60},
                            delay: 250,
                            noData: _t("No Data Available."),
                            transition: 500,
                            valueFormat: d3.format(',.2f'),
                            showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
                            showXAxis: true,
                            showYAxis: true,
                            rightAlignYAxis: false,
                            stacked: this.stacked,
                            reduceXTicks: false,
                            rotateLabels: -20,
                            showControls: false,
                            color: d3.scale.category10().range(),
                        });
                        chart.x(function (d) {
                            return d.label
                        })
                        .y(function (d) {
                           return d.value
                        })
                        .margin({
                            top: 30,
                            right: 20,
                            bottom: 50,
                            left: 85
                        });
                        chart.yAxis.tickFormat(d3.format(',.02f'));
                        chart.yAxis.tickSize(20);

                        break;
                }
                chart(svg);
                nv.utils.onWindowResize(chart.update);
                if (chart) {
                    self.charts.push(chart);
                    chart.tooltip.chartContainer(container[0]);
                }
            });
        },
        destroy: function () {
            if (this.charts) {
                for (var i = 0; i < this.charts.length; i++) {
                    nv.utils.offWindowResize(this.charts[i].update);
                }
            }
            this._super();
        },

    });

    var CmiFilterSelection = form_common.AbstractField.extend(form_common.ReinitializeFieldMixin, {
        template: 'CmiFilterSelection',
        events: {
            'change': 'store_dom_value',
        },
        init: function (field_manager, node) {
            this._super(field_manager, node);
            this.set("value", false);
            this.set("values", []);
            this.records_orderer = new utils.DropMisordered();
            this.field_manager.on("view_content_has_changed", this, function () {
                var domain = new data.CompoundDomain(this.build_domain()).eval();
                if (!_.isEqual(domain, this.get("domain"))) {
                    this.set("domain", domain);
                }
            });
        },
        initialize_field: function () {
            form_common.ReinitializeFieldMixin.initialize_field.call(this);
            this.on("change:domain", this, this.query_values);
            this.set("domain", new data.CompoundDomain(this.build_domain()).eval());
            this.on("change:values", this, this.render_value);
        },
        query_values: function () {
            var self = this;
            var def;
            if (this.field.type === "many2one") {
                var model = new Model(this.field.relation);
                def = model.call("name_search", ['', this.get("domain")], {"context": this.build_context()});
            } else {
                var values = _.reject(this.field.selection, function (v) {
                    return v[0] === false && v[1] === '';
                });
                def = $.when(values);
            }
            this.records_orderer.add(def).then(function (values) {
                if (!_.isEqual(values, self.get("values"))) {
                    self.set("values", values);
                }
            });
        },
        initialize_content: function () {
            // Flag indicating whether we're in an event chain containing a change
            // event on the select, in order to know what to do on keyup[RETURN]:
            // * If the user presses [RETURN] as part of changing the value of a
            //   selection, we should just let the value change and not let the
            //   event broadcast further (e.g. to validating the current state of
            //   the form in editable list view, which would lead to saving the
            //   current row or switching to the next one)
            // * If the user presses [RETURN] with a select closed (side-effect:
            //   also if the user opened the select and pressed [RETURN] without
            //   changing the selected value), takes the action as validating the row
            // if (!this.get('effective_readonly')) {
            var ischanging = false;
            this.$el
                .change(function () {
                    ischanging = true;
                })
                .click(function () {
                    ischanging = false;
                })
                .keyup(function (e) {
                    if (e.which !== 13 || !ischanging) {
                        return;
                    }
                    e.stopPropagation();
                    ischanging = false;
                });
            this.setupFocus(this.$el);
            // }
        },
        commit_value: function () {
            this.store_dom_value();
            return this._super();
        },
        store_dom_value: function () {
            // if (!this.get('effective_readonly')) {
            this.internal_set_value(JSON.parse(this.$el.val()));
            // }
            //To avoid form became dirty
            this.view.$el.removeClass('oe_form_dirty');
        },
        set_value: function (value_) {
            value_ = value_ === null ? false : value_;
            value_ = value_ instanceof Array ? value_[0] : value_;
            this._super(value_);
        },
        render_value: function () {
            var values = this.get("values");
            values = [[this.node.attrs.placeholder || '']].concat(values);
            var found = _.find(values, function (el) {
                return el[0] === this.get("value");
            }, this);
            if (!found) {
                found = [this.get("value"), _t('Unknown')];
                values = [found].concat(values);
            }
            // if (!this.get("effective_readonly")) {
            this.$el.empty();
            for (var i = 0; i < values.length; i++) {
                this.$el.append($('<option/>', {
                    value: JSON.stringify(values[i][0]),
                    html: values[i][1]
                }))
            }
            this.$el.val(JSON.stringify(found[0]));
            // } else {
            //     this.$el.text(found[1]);
            // }
        },
        focus: function () {
            // if (!this.get("effective_readonly")) {
            return this.$el.focus();
            // }
        },
    });

    core.form_widget_registry.add('cmi_filter_selection', CmiFilterSelection);
    core.form_widget_registry.add('cmi_dashboard', CMIDashboardWidget);
    return {CMIDashboardWidget: CMIDashboardWidget};
});