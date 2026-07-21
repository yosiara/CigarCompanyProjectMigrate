/** @odoo-module **/
import { FormRenderer } from "@web/views/form/form_renderer";
import { Field } from "@web/views/fields/field";

export class ComputerFormRenderer extends FormRenderer {
    static template = "ict.ComputerFormRenderer";
    static components = {
        ...FormRenderer.components,
        Field,  // Aseguramos que Field esté disponible
    };

    setup() {
        super.setup();
        // No necesitamos templates.FormRenderer
    }

    async onChangeState(newState) {
        await this.props.record.update({ state: newState });
    }

    // Helper para obtener el valor de un campo (útil para la tarjeta resumen)
    getFieldValue(fieldName) {
        return this.props.record.data[fieldName];
    }
}