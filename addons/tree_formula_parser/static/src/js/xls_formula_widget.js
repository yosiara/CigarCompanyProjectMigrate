/**
 * Created by vladimir on 12/12/17.
 */

odoo.define('tree_formula_parser.xls_formula_widget', function (require) {
    "use strict";

    var core = require('web.core');
    var form_widgets = require('web.form_widgets');
    var FieldFloat = form_widgets.FieldFloat;
    var parser = new formulaParser.Parser();

    var formulaParserXls = FieldFloat.extend({
        store_dom_value:function(){
            if (this.$input && this.is_syntax_valid()) {
                var res_apply = parser.parse(this.$input.val());
                if (res_apply['error'] == null) {
                    this.internal_set_value(this.parse_value(res_apply['result']));
                }
                else{
                    alert(res_apply['error']);
                }
            }
        },
    });

    core.form_widget_registry.add('xls_formula', formulaParserXls);

    return formulaParserXls;
});