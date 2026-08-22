import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { MobileKanbanRenderer } from "./mobile_kanban_renderer";

// Registrar la vista personalizada
export const MobileKanbanView = {
    ...kanbanView,
    Renderer: MobileKanbanRenderer,
};

registry.category("views").add("mobile_kanban", MobileKanbanView);