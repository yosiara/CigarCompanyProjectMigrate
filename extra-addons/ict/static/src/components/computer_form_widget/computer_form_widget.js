/** @odoo-module **/

import { Widget } from "@web/legacy/js/framework/widget";
import { Component, useState, onWillUpdateProps, xml } from "@odoo/owl";
import { registry } from "@web/core/registry";

// Componente Owl para el formulario moderno
class ComputerFormOwl extends Component {
    setup() {
        this.state = useState({
            record: this.props.record,
        });
        onWillUpdateProps((nextProps) => {
            this.state.record = nextProps.record;
        });
    }

    static template = xml`
        <div class="computer-modern-form">
            <div class="form-header" t-att-class="state.state">
                <div class="header-content">
                    <h1><t t-esc="state.record.data.name"/></h1>
                    <span class="badge" t-att-class="'badge-' + state.record.data.state">
                        <t t-esc="state.record.data.state.replace('_', ' ').toUpperCase()"/>
                    </span>
                </div>
            </div>

            <div class="form-body">
                <!-- Tarjeta de especificaciones -->
                <div class="specs-card">
                    <div class="spec-icon">
                        <i t-attf-class="fa {{ state.record.data.type === 'laptop' ? 'fa-laptop' : (state.record.data.type === 'desktop' ? 'fa-desktop' : 'fa-server') }}"></i>
                    </div>
                    <div class="spec-details">
                        <div class="spec-item">
                            <label>Procesador:</label>
                            <span><t t-esc="state.record.data.processor_name || 'N/A'"/></span>
                        </div>
                        <div class="spec-item">
                            <label>RAM:</label>
                            <span><t t-esc="state.record.data.total_memory_gb || 0"/> GB</span>
                        </div>
                        <div class="spec-item">
                            <label>Almacenamiento:</label>
                            <span><t t-esc="state.record.data.total_storage_gb || 0"/> GB</span>
                        </div>
                    </div>
                </div>

                <!-- Campos agrupados -->
                <div class="fields-grid">
                    <div class="field-group">
                        <label>Marca</label>
                        <input type="text" t-model="state.record.data.brand" class="form-control"/>
                    </div>
                    <div class="field-group">
                        <label>Modelo</label>
                        <input type="text" t-model="state.record.data.model" class="form-control"/>
                    </div>
                    <div class="field-group">
                        <label>Sistema Operativo</label>
                        <select t-model="state.record.data.operating_system" class="form-control">
                            <option value="windows_10">Windows 10</option>
                            <option value="windows_11">Windows 11</option>
                            <option value="linux">Linux</option>
                            <option value="macos">macOS</option>
                        </select>
                    </div>
                    <div class="field-group">
                        <label>IP Address</label>
                        <input type="text" t-model="state.record.data.ip_address" class="form-control"/>
                    </div>
                    <!-- más campos -->
                </div>

                <!-- Pestañas Owl (opcional) -->
                <div class="owl-tabs">
                    <div class="tab-headers">
                        <button t-att-class="state.activeTab === 'components' ? 'active' : ''" t-on-click="() => state.activeTab = 'components'">Componentes</button>
                        <button t-att-class="state.activeTab === 'applications' ? 'active' : ''" t-on-click="() => state.activeTab = 'applications'">Aplicaciones</button>
                    </div>
                    <div class="tab-content">
                        <div t-if="state.activeTab === 'components'">
                            <!-- Mostrar componentes -->
                            <div t-foreach="state.record.data.component_ids" t-as="comp" t-key="comp.id">
                                <t t-esc="comp.name"/>
                            </div>
                        </div>
                        <div t-else-if="state.activeTab === 'applications'">
                            <!-- Aplicaciones -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Widget que integra el componente Owl en la vista form
export class ComputerFormWidget extends Widget {
    static selector = '.computer_form_owl';
    static template = 'ComputerFormWidgetTemplate';

    init() {
        this.record = this.record || {};
    }

    start() {
        // Crear el componente Owl y montarlo en el elemento
        const element = this.el;
        const recordData = this.record.data;
        const owlComponent = new ComputerFormOwl();
        owlComponent.props = { record: this.record };
        owlComponent.mount(element);
        return owlComponent;
    }
}

// Registrar el widget en la interfaz de Odoo
registry.category('widgets').add('computer_form_widget', ComputerFormWidget);