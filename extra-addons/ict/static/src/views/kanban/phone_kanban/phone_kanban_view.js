import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { PhoneKanbanRenderer } from "./phone_kanban_renderer";

// Registrar la vista personalizada
export const PhoneKanbanView = {
    ...kanbanView,
    Renderer: PhoneKanbanRenderer,
};

registry.category("views").add("phone_kanban", PhoneKanbanView);