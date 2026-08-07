/** @odoo-module **/
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { useService } from "@web/core/utils/hooks";
import { onWillStart, onMounted, useState } from "@odoo/owl";
import { ComputerKanbanRecord } from "./computer_kanban_record";

export class ComputerKanbanRenderer extends KanbanRenderer {
    static template = "ict.ComputerKanbanRenderer";
    static components = {
        ...KanbanRenderer.components,
        KanbanRecord: ComputerKanbanRecord,
    };

    setup() {
        super.setup();
        // this.orm = useService("orm");
        // this.action = useService("action");
        // this.notification = useService("notification");

        // this.headState = useState({
        //     stats: {},
        //     loading: true,
        //     searchTerm: '',
        //     activeFilter: 'all',
        // });
        // this.headState.stats = this.headState.stats || {};
        // this.headState.loading = this.headState.loading || true;
        // this.headState.searchTerm = this.headState.searchTerm || '';
        // this.headState.activeFilter = this.headState.activeFilter || 'all';
        
        // onWillStart(async () => {
        //     await this.loadStats();
        // });
        
        // onMounted(() => {
        //     this.setupSearchListener();
        // });
    }

    async loadStats() {
        this.headState.loading = true;
        try {
            const stats = await this.orm.call("ict.computer", "get_kanban_stats", []);
            
            // Calcular tendencias (ejemplo)
            const lastMonthStats = await this.orm.call("ict.computer", "get_kanban_stats", [{
                last_month: true
            }]);
            
            // Enriquecer stats con tendencias
            Object.assign(this.headState.stats, stats, {
                trends: this.calculateTrends(stats, lastMonthStats)
            });
            
        } catch (error) {
            this.notification.add(
                "Error loading dashboard statistics",
                { type: "danger" }
            );
            console.error("Error loading kanban stats:", error);
        } finally {
            this.headState.loading = false;
        }
    }

    calculateTrends(current, previous) {
        const trends = {};
        if (previous && previous.total) {
            trends.total = ((current.total - previous.total) / previous.total * 100).toFixed(1);
        }
        return trends;
    }

    setupSearchListener() {
        // Implementar búsqueda en tiempo real
        const searchInput = document.querySelector('.search-box input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.headState.searchTerm = e.target.value.toLowerCase();
                this.filterRecords();
            });
        }

        // Filtros rápidos
        document.querySelectorAll('.btn-filter').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.btn-filter').forEach(b => 
                    b.classList.remove('active')
                );
                btn.classList.add('active');
                this.headState.activeFilter = btn.dataset.filter;
                this.filterRecords();
            });
        });
    }

    filterRecords() {
        // Filtrar registros del kanban
        const records = document.querySelectorAll('.o_kanban_record');
        records.forEach(record => {
            const card = record.querySelector('.ict-kanban-card');
            const title = card?.querySelector('h3')?.textContent.toLowerCase() || '';
            const model = card?.querySelector('.model')?.textContent.toLowerCase() || '';
            const status = card?.querySelector('.status-badge span')?.textContent.toLowerCase() || '';
            
            const matchesSearch = title.includes(this.headState.searchTerm) || 
                                 model.includes(this.headState.searchTerm);
            const matchesFilter = this.headState.activeFilter === 'all' || 
                                status.includes(this.headState.activeFilter.replace('_', ' '));
            
            record.style.display = matchesSearch && matchesFilter ? 'block' : 'none';
        });
    }

    getStatusClass(status) {
        const classes = {
            'available': 'success',
            'assigned': 'info',
            'repair': 'warning',
            'retired': 'secondary'
        };
        return classes[status] || 'primary';
    }

    getStatusIcon(status) {
        const icons = {
            'available': 'fa-star',
            'assigned': 'fa-play-circle',
            'repair': 'fa-wrench',
            'retired': 'fa-archive'
        };
        return icons[status] || 'fa-circle';
    }

    async onCardClick(record) {
        // Acción al hacer clic en la tarjeta
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'ict.computer',
            res_id: record.id,
            views: [[false, 'form']],
            target: 'current'
        });
    }

    async onButtonClick(action, recordId, event) {
        event.stopPropagation();
        
        switch(action) {
            case 'view':
                await this.onCardClick({id: recordId});
                break;
            case 'edit':
                await this.action.doAction({
                    type: 'ir.actions.act_window',
                    res_model: 'ict.computer',
                    res_id: recordId,
                    views: [[false, 'form']],
                    target: 'current',
                    context: { form_view_ref: 'ict_computer.view_ict_computer_form' }
                });
                break;
            case 'maintenance':
                // Acción de mantenimiento
                this.notification.add(
                    "Maintenance request sent",
                    { type: "success" }
                );
                break;
        }
    }
}

// ComputerKanbanRenderer.template = "ict.ComputerKanbanRenderer";