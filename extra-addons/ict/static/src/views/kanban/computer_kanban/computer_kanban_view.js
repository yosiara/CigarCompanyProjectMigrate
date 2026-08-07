import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { ComputerKanbanRenderer } from "./computer_kanban_renderer";

// Registrar la vista personalizada
export const ComputerKanbanView = {
    ...kanbanView,
    Renderer: ComputerKanbanRenderer,
};

registry.category("views").add("computer_kanban", ComputerKanbanView);