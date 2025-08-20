/** @odoo-module **/

import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanView } from "@web/views/kanban/kanban_view";
import { registry } from "@web/core/registry";
import { Component, onWillStart, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

// Controller
export class MachineKanbanController extends KanbanController {
    setup() {
        super.setup();
        // this.orm = useService("orm");
        // this.state = useState({
        //     selectedMachine: null,
        // });
    }

    // Método para manejar la selección de máquina
    // async selectMachine(machine) {
    //     this.state.selectedMachine = machine;
        
    //     // Aplicar filtro si es necesario
    //     if (machine) {
    //         // Tu lógica de filtrado aquí
    //         console.log("Máquina seleccionada:", machine);
    //     }
    // }

    // clearFilter() {
    //     this.state.selectedMachine = null;
    // }
}

MachineKanbanController.template = "process_control.MachineKanbanView";

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
    }
}
MachineKanbanView.template = "process_control.MachineKanbanView";
MachineKanbanView.components = {
    ...KanbanView.components,
    MachineKanbanComponent,
};
MachineKanbanView.Controller = MachineKanbanController;

// Registrar la vista
registry.category("views").add("process_control_machine_kanban", MachineKanbanView);