/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class AssignmentTimeline extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            assignments: [],
            viewMode: 'month', // 'week', 'month', 'year'
            selectedDate: new Date()
        });

        onWillStart(async () => {
            await this.loadAssignments();
        });
    }

    async loadAssignments() {
        const domain = this.buildDateDomain();
        const computers = await this.orm.searchRead(
            "ict.computer",
            domain,
            ['name', 'employee_id', 'assignment_date', 'brand', 'model']
        );
        
        const phones = await this.orm.searchRead(
            "ict.phone",
            domain,
            ['name', 'employee_id', 'assignment_date', 'brand', 'model']
        );

        this.state.assignments = [
            ...computers.map(c => ({...c, type: 'computer'})),
            ...phones.map(p => ({...p, type: 'phone'}))
        ].sort((a, b) => new Date(a.assignment_date) - new Date(b.assignment_date));
    }

    buildDateDomain() {
        const date = this.state.selectedDate;
        let start, end;
        
        switch(this.state.viewMode) {
            case 'week':
                start = new Date(date.setDate(date.getDate() - date.getDay()));
                end = new Date(date.setDate(date.getDate() - date.getDay() + 6));
                break;
            case 'month':
                start = new Date(date.getFullYear(), date.getMonth(), 1);
                end = new Date(date.getFullYear(), date.getMonth() + 1, 0);
                break;
            case 'year':
                start = new Date(date.getFullYear(), 0, 1);
                end = new Date(date.getFullYear(), 11, 31);
                break;
        }
        
        return [
            ['assignment_date', '>=', start],
            ['assignment_date', '<=', end]
        ];
    }

    getIcon(type) {
        return type === 'computer' ? 'fa-laptop' : 'fa-mobile';
    }

    getColor(type) {
        return type === 'computer' ? 'primary' : 'success';
    }
}

AssignmentTimeline.template = "ict.AssignmentTimeline";