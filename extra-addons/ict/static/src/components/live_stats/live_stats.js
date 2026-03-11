/** @odoo-module **/
import { Component, useState, onWillStart, onWillDestroy } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class LiveStats extends Component {
    setup() {
        this.orm = useService("orm");
        this.bus = useService("bus_service");
        
        this.state = useState({
            stats: {
                computers_in_use: 0,
                available_phones: 0,
                employees_without_computer: 0,
                expiring_warranties: [],
                recent_activities: []
            },
            lastUpdate: new Date()
        });

        onWillStart(async () => {
            await this.refreshStats();
            this.startPolling();
        });

        onWillDestroy(() => {
            if (this.pollingInterval) {
                clearInterval(this.pollingInterval);
            }
        });
    }

    startPolling() {
        // Actualizar cada 30 segundos
        this.pollingInterval = setInterval(() => {
            this.refreshStats();
        }, 30000);
    }

    async refreshStats() {
        const stats = await this.orm.call("ict.reports", "get_live_stats", []);
        Object.assign(this.state.stats, stats);
        this.state.lastUpdate = new Date();
    }

    getTimeSinceUpdate() {
        const seconds = Math.floor((new Date() - this.state.lastUpdate) / 1000);
        return `${seconds} seconds ago`;
    }
}

LiveStats.template = "ict.LiveStats";