# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WorkOrder(models.Model):
    _name = 'maintenance_turei.work_order'
    _description = 'maintenance_turei.work_order'
    _rec_name = 'number_new'

    code = fields.Char(required=True, string='Código')
    number = fields.Char(string='Número')
    number_new = fields.Char("Número")

    opening_date = fields.Date(readonly=False, string='Fecha Apertura')
    closing_date = fields.Date(readonly=False, string='Fecha Cierre')

    execute_cost_center_id = fields.Many2one('base_cu.cost_center', string='Ejecuta', required=True)
    receive_cost_center_id = fields.Many2one('base_cu.cost_center', string='Recibe', required=True)
    state = fields.Selection([('created', 'Creada'), ('open', 'Abierta'), ('closed', 'Cerrada'), ('cancel', 'Cancelada')], default='created', readonly=True, string='Estado')
    # type_id = fields.Many2one('atmsys.work_order.type', string='Tipo', required=True, readonly=False)

    creator_id = fields.Many2one('hr.employee', string='Abre', readonly=True)
    emitter_id = fields.Many2one('hr.employee', string='Emite', required=True)
    executor_id = fields.Many2one('hr.employee', string='Ejecuta', required=True)
    shutter_id = fields.Many2one('hr.employee', string='Cierra', readonly=True)

    realized_work_ids = fields.One2many(comodel_name="maintenance_turei.realized_work", inverse_name="realized_work_order_id",
                                    string="Trabajo Realizado", required=False, ondelete='cascade')
    equipament_id = fields.Many2one('maintenance.equipment', string='Equipo', domain="[('is_industrial', '=', True)]")
    cycle_id = fields.Many2one('maintenance_turei.cycle_maintenance', string='Ciclo', domain="[('equipment_id', '=', equipament_id)]")
    maintenance_request_id = fields.Many2one('maintenance.request', string='Petición de Mantenimiento')
    equipment_or_area = fields.Char(string="Equipo según ATM")
    note = fields.Text(string="Descripción")

    product_order_ids = fields.One2many('maintenance_turei.product_order', inverse_name='work_order_id', string='Productos...')
    #ESte campo hay que declararlo en Work order de ATM
    # work_order_mtto_id = fields.Many2one('maintenance_turei.work_order', string='WOMTTO')

    anir = fields.Boolean(default=False)
    time = fields.Char(string='Tiempo(Hr)')
    ready_equipment = fields.Selection([('si', 'SI'), ('no', 'NO')], string='Equipo Listo')
    work_type = fields.Selection([('imp-tec', 'Imprevisto-Técnico'), ('imp_ope', 'Imprevisto-Por Operación'),
                                  ('plan_ciclo', 'Planificado-Ciclo'), ('plan_et', 'Planificado x Estado Técnico'),
                                  ('ins_tec', 'Inspección Técnica')], string='Tipo de Trabajo')
    delivered = fields.Boolean(string="Entregada")
    category_id = fields.Many2one(related='equipament_id.category_id', store=True)
    maintenance_team_id = fields.Many2one(related='equipament_id.maintenance_team_id', store=True)
    line_id = fields.Many2one(related='equipament_id.line_id')
    description_cancel = fields.Char('Motivo')
    user_cancel_id = fields.Many2one('res.users', 'Usuario')
    date_cancel = fields.Datetime('Fecha y Hora')

    def button_request(self):
        if self.maintenance_request_id:
            self.maintenance_request_id.write({'stage_id': self.env.ref('maintenance.stage_3').id})
        else:
            raise ValidationError('Debe añadir una Petición de Mantenimiento a la orden de trabajo.')

    @api.onchange('equipament_id', 'cycle_id')
    def _onchange_equipment_cycle_id(self):
        year = datetime.today().date().year
        mr_ids = self.env['maintenance.request'].search([('equipment_id', '=', self.equipament_id.id), ('cycle_id', '=', self.cycle_id.id), ('year_char', '=', str(year))])
        return {
            'domain': {
                'maintenance_request_id': [('id', 'in', mr_ids.ids)]
            }
        }

    # def button_open(self):
    #     self.state = 'open'
    #     self.closing_date = None
    #
    #     if not self.opening_date:
    #         self.opening_date = fields.Date.today()
    #
    #     employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
    #     if len(employees):
    #         self.creator_id = employees[0].id
    #
    # def button_close(self):
    #     self.state = 'closed'
    #     self.closing_date = fields.Date.today()
    #
    #     employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
    #     if len(employees):
    #         self.shutter_id = employees[0].id

    # Estos metodos van en el work order de ATM
    # Hay que declarar un nuevo campo work_order_mtto_id en el work order de ATM
    # @api.model
    # def create(self, vals):
    #     work_order = super(WorkOrder, self).create(vals)
    #     if vals.get('type_id'):
    #         if work_order.type_id.name == 'A' or work_order.type_id.name == 'P':
    #             if vals.get('product_order_ids'):
    #                 list_product = []
    #                 for line in work_order.product_order_ids:
    #                     list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
    #                 vals['product_order_ids'] = list_product
    #             work_order_mtto = self.env['maintenance_turei.work_order'].sudo().create(vals)
    #             work_order.write({'work_order_mtto_id': work_order_mtto.id})
    #     return work_order
    # #
    # @api.model_create_multi
    # def write(self, vals):
    #     res = super(WorkOrder, self).write(vals)
    #     work_order = self.env['maintenance_turei.work_order'].browse(self.work_order_mtto_id.id)
    #     if vals.get('type_id'):
    #         if work_order.type_id.name == 'A' or work_order.type_id.name == 'P':
    #             if vals.get('product_order_ids'):
    #                 work_order.product_order_ids.unlink()
    #                 list_product = []
    #                 for line in self.product_order_ids:
    #                     list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
    #                 vals['product_order_ids'] = list_product
    #             work_order.write(vals)
    #     return res