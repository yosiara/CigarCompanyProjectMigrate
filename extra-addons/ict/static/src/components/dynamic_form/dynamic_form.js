/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class DynamicComputerForm extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            computer: {
                name: "",
                brand: "",
                model: "",
                type: "desktop",
                ram_gb: 8,
                storage_gb: 256,
                employee_id: false,
                state: "new"
            },
            employees: [],
            showAdvanced: false,
            saving: false
        });

        onWillStart(async () => {
            await this.loadEmployees();
        });
    }

    async loadEmployees() {
        this.state.employees = await this.orm.searchRead(
            "ict.employee",
            [('active', '=', true)],
            ['name', 'department_id']
        );
    }

    async saveComputer() {
        this.state.saving = true;
        try {
            const result = await this.orm.create("ict.computer", [this.state.computer]);
            this.action.doAction({
                type: 'ir.actions.act_window_close',
            });
            // Mostrar notificación de éxito
            this.env.services.notification.add('Computer created successfully!', {
                type: 'success',
            });
        } catch (error) {
            this.env.services.notification.add('Error creating computer', {
                type: 'danger',
            });
        } finally {
            this.state.saving = false;
        }
    }

    updateField(fieldName, value) {
        this.state.computer[fieldName] = value;
        this.trigger('field-changed', { field: fieldName, value });
    }
}

DynamicComputerForm.template = "ict.DynamicComputerForm";