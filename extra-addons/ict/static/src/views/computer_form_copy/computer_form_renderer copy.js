/** @odoo-module **/
import { FormRenderer } from "@web/views/form/form_renderer";

export class ComputerFormRenderer extends FormRenderer {
    static template = "ict.ComputerFormRenderer";

    setup() {
        super.setup();
        // Puedes agregar estado reactivo aquí si lo necesitas
    }

    // Método para cambiar el estado (ejemplo)
    async onChangeState(newState) {
        await this.props.record.update({ state: newState });
    }
}