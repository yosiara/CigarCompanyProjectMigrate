/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class StatusBadgeField extends Component {
    setup() {
        super.setup();
        this.statusMap = {
            'online': { 
                cssClass: 'status-online',
                label: 'En línea'
            },
            'offline': { 
                cssClass: 'status-offline',
                label: 'Desconectado'
            },
            'away': { 
                cssClass: 'status-away',
                label: 'Ausente'
            },
            'busy': { 
                cssClass: 'status-busy',
                label: 'Ocupado'
            }
        };
    }

    get statusInfo() {
        var status = this.props.record.data[this.props.name] || 'offline';
        return this.statusMap[status] || this.statusMap['offline'];
    }

    get statusClass() {
        return this.statusInfo.cssClass;
    }

    get statusLabel() {
        return this.statusInfo.label;
    }
}

StatusBadgeField.template = 'ict.StatusBadgeField';
StatusBadgeField.props = {
    ...standardFieldProps,
};

export const statusBadgeField = {
    component: StatusBadgeField
};

registry.category("fields").add("ict_status_badge", statusBadgeField);