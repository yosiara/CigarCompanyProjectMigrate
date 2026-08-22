import { KanbanRecord } from "@web/views/kanban/kanban_record";

export class MobileKanbanRecord extends KanbanRecord {
    setup() {
        super.setup();
    }

    getRecordClasses() {
        let classes = super.getRecordClasses();
        return classes + " custom_kanban_record";
    }
}