/** @odoo-module */

import { createWebClient } from "@web/../tests/webclient/helpers";
import { WebClientCommunity } from "@web_community/webclient/webclient";

export function createCommunityWebClient(params) {
    params.WebClientClass = WebClientCommunity;
    return createWebClient(params);
}
