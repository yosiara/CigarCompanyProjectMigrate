/** @odoo-module **/

import { startWebClient } from "@web/start";
import { WebClientCommunity } from "./webclient/webclient";

/**
 * This file starts the community webclient. In the manifest, it replaces
 * the community main.js to load a different webclient class
 * (WebClientCommunity instead of WebClient)
 */
startWebClient(WebClientCommunity);
