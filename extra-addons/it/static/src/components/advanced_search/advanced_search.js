/** @odoo-module **/
import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AdvancedSearch extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            searchTerm: "",
            filters: {
                department: "",
                status: "",
                type: ""
            },
            results: [],
            showResults: false
        });
    }

    async search() {
        this.state.showResults = true;
        const domain = this.buildDomain();
        this.state.results = await this.orm.searchRead(
            this.props.model,
            domain,
            ['name', 'display_name', 'model_field'],
            { limit: 10 }
        );
    }

    buildDomain() {
        let domain = [];
        if (this.state.searchTerm) {
            domain.push(['name', 'ilike', this.state.searchTerm]);
        }
        if (this.state.filters.department) {
            domain.push(['department_id', '=', this.state.filters.department]);
        }
        if (this.state.filters.status) {
            domain.push(['state', '=', this.state.filters.status]);
        }
        return domain;
    }

    selectResult(result) {
        this.env.bus.trigger('record-selected', result);
        this.state.showResults = false;
    }
}

AdvancedSearch.template = "it.AdvancedSearch";