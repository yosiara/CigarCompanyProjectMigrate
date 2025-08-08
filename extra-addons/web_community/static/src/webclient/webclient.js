/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";
import { CommunityNavBar } from "./navbar/navbar";

export class WebClientCommunity extends WebClient {
    setup() {
        super.setup();
        this.hm = useService("home_menu");
    }
    _loadDefaultApp() {
        return this.hm.toggle(true);
    }
}
WebClientCommunity.components = { ...WebClient.components, NavBar: CommunityNavBar };
