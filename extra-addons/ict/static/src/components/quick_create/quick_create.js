/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class QuickCreate extends Component {
    setup() {
        this.orm = useService("orm");
        this.dialog = useService("dialog");
        
        this.state = useState({
            activeTab: 'computer',
            forms: {
                computer: {
                    name: '',
                    brand: '',
                    employee_id: false
                },
                employee: {
                    name: '',
                    domain_user: '',
                    email: ''
                },
                phone: {
                    name: '',
                    brand: '',
                    number: ''
                }
            }
        });
    }

    async quickCreate() {
        const data = this.state.forms[this.state.activeTab];
        const model = `ict.${this.state.activeTab}`;
        
        try {
            const id = await this.orm.create(model, [data]);
            this.env.bus.trigger('record-created', {
                model: model,
                id: id,
                data: data
            });
            
            // Reset form
            this.resetForm();
            
            // Mostrar mensaje de éxito
            this.dialog.add({
                title: 'Success',
                body: `${this.state.activeTab} created successfully!`,
                type: 'success'
            });
            
        } catch (error) {
            this.dialog.add({
                title: 'Error',
                body: error.message,
                type: 'danger'
            });
        }
    }

    resetForm() {
        this.state.forms[this.state.activeTab] = Object.keys(
            this.state.forms[this.state.activeTab]
        ).reduce((acc, key) => ({...acc, [key]: ''}), {});
    }
}

QuickCreate.template = "ict.QuickCreate";