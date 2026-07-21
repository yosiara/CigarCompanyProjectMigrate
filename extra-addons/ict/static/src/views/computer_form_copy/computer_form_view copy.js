/** @odoo-module **/
import { registry } from "@web/core/registry";
import { FormView } from "@web/views/form/form_view";
import { ComputerFormRenderer } from "./computer_form_renderer";

export const ComputerFormView = {
    ...FormView,
    Renderer: ComputerFormRenderer,
};

registry.category("views").add("computer_form", ComputerFormView);