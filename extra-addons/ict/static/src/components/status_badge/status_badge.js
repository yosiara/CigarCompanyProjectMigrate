/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

export class StatusBadgeField extends Component {
    setup() {
        super.setup();
        this.statusMap = {
            'active': { 
                cssClass: 'status-online',
                label: 'Confirmed'
            },
            'new': { 
                cssClass: 'status-offline',
                label: 'Never Connected'
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
        var status = this.props.record.data[this.props.name] || 'new';
        return this.statusMap[status] || this.statusMap['new'];
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