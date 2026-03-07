/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class ITDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            stats: {
                total_employees: 0,
                total_computers: 0,
                total_phones: 0,
                active_services: 0,
                computers_by_state: [],
                recent_assignments: []
            },
            loading: true
        });

        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        try {
            // Load general statistics
            const stats = await this.orm.call(
                "it.reports",
                "get_dashboard_stats",
                []
            );
            
            Object.assign(this.state.stats, stats);
            this.state.loading = false;
            
        } catch (error) {
            console.error("Error loading dashboard:", error);
            this.state.loading = false;
        }
    }

    getStatusClass(state) {
        const classes = {
            'new': 'text-success',
            'in_use': 'text-primary',
            'repair': 'text-warning',
            'retired': 'text-danger',
            'available': 'text-success',
            'assigned': 'text-primary'
        };
        return classes[state] || 'text-secondary';
    }
}

ITDashboard.template = "it.Dashboard";

// Register the component
registry.category("actions").add("it_dashboard", ITDashboard);