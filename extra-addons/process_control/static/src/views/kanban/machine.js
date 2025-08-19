/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { Component, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Component
export class MachineKanbanComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            machines: [],
            selectedMachine: null,
        });

        onWillStart(async () => {
            await this.loadMachines();
        });
    }

    async loadMachines() {
        try {
            this.state.machines = await this.orm.searchRead("process_control.machine",[]);
        } catch (error) {
            console.error("Error loading machines:", error);
        }
    }

    handleCustomerClick(machine) {
        this.state.selectedMachine = machine.id;
        this.props.selectMachine(machine);
    }

    clearSelection() {
        this.state.selectedMachine = null;
        this.props.selectMachine(null);
    }
}
MachineKanbanComponent.template = "process_control.MachineKanbanComponent";
MachineKanbanComponent.props = {
    selectMachine: { type: Function },
};

// View
export class MachineKanbanView extends KanbanView {
    setup() {
        super.setup();
        this.components = {
            ...this.components,
            MachineKanbanComponent,
        };
    }
}
MachineKanbanView.components = {
    ...KanbanView.components,
    MachineKanbanComponent,
};
MachineKanbanView.Controller = KanbanController;

export const MachineKanbanViewObject = {
    ...kanbanView,
    MachineKanbanView,
};

// Registrar la vista
registry.category("views").add("machine_kanban_view", MachineKanbanViewObject);