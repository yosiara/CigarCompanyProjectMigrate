odoo.define('cmi_kanban_gauge.widget', function (require) {
"use strict";

var core = require('web.core');
var kanban_widgets = require('web_kanban.widgets');
var utils = require('web.utils');

var AbstractField = kanban_widgets.AbstractField;
var fields_registry = kanban_widgets.registry;
var _t = core._t;

var GaugeWidget = AbstractField.extend({
    className: "cmi_gauge",

    start: function() {
        var self = this;
        var parent = this.getParent();
        // // parameters
        var value = this.options.value || 0;
        if (this.options.value_field) {
            value = this.getParent().record[this.options.value_field].raw_value;
        }
        var max_value = this.options.max_value || 100;
        if (this.options.max_field) {
            max_value = this.getParent().record[this.options.max_field].raw_value;
        }
        var min_value = this.options.min_value || 0;
        if (this.options.min_field) {
            min_value = this.getParent().record[this.options.min_field].raw_value;
        }
        var first_zone_limit_value = this.options.first_zone_limit_value || 0;
        if (this.options.first_zone_limit_field) {
            first_zone_limit_value = this.getParent().record[this.options.first_zone_limit_field].raw_value;
        }
        var second_zone_limit_value = this.options.second_zone_limit_value || 0;
        if (this.options.second_zone_limit_field) {
            second_zone_limit_value = this.getParent().record[this.options.second_zone_limit_field].raw_value;
        }
        var optimal_value = this.options.optimal_value || 0;
        if (this.options.optimal_value_field) {
            optimal_value = this.getParent().record[this.options.optimal_value_field].raw_value;
        }
        var uom_value = this.options.uom_value || 0;
        if (this.options.uom_field) {
            uom_value = this.getParent().record[this.options.uom_field].raw_value;
        }
        var color;
        if(optimal_value == 'min'){
            color = ['#88ac67', '#f78f20', '#db4e4e']
        }else if (optimal_value == 'max'){
            color = ['#db4e4e', '#f78f20', '#88ac67'];
        }else{
            color = ['#db4e4e', '#88ac67', '#db4e4e'];
        }

        this.$el.empty().attr('style', this.$node.attr('style') + ';position:relative; display:inline-block;');
        var container = this.$el[0];
        nv.addGraph(function() {
            var chart = nv.models.gaugeChart()
                .margin({'top': 5})
                .min(min_value)
                .max(max_value)
                .zoneLimit1(first_zone_limit_value)
                .zoneLimit2(second_zone_limit_value)
                .color(color)
                .uom(uom_value);

            d3.select(container)
                .append("svg")
                .datum([value])
                .call(chart);

            nv.utils.windowResize(chart.update);
            return chart;
        });

    },
});

fields_registry.add("cmi_gauge", GaugeWidget);

});
