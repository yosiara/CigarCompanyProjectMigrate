/** @odoo-module */

import { registry } from "@web/core/registry";
import { standardWidgetProps } from "@web/views/widgets/standard_widget_props";

import { useOpenChat } from "@mail/core/web/open_chat_hook";
import { Component } from "@odoo/owl";

export class ICTEmployeeChat extends Component {
    static props = {
        ...standardWidgetProps,
    };
    static template = "ict.OpenChat";

    setup() {
        super.setup();
        this.openChat = useOpenChat(this.props.record.resModel);
    }
}

export const ictEmployeeChat = {
    component: ICTEmployeeChat,
};
registry.category("view_widgets").add("ict_employee_chat", ictEmployeeChat);
