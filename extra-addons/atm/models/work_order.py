# -*- coding: utf-8 -*-

from odoo import api
from odoo.exceptions import ValidationError
from odoo.models import Model
from odoo.fields import Char, Text, Date, Many2one, Selection, One2many, Boolean, Datetime
from odoo.tools.translate import _


class WorkOrder(Model):
    _inherit = ['mail.thread']
    _name = 'atm.work_order'
    _description = 'atm.work_order'
    _rec_name = 'number_new'

    def _get_code(self):
        work_orders = self.search([], limit=1, order='opening_date DESC, code DESC')
        if not len(work_orders):
            return '00001'

        temp = int(work_orders[0].code)
        rep = str(temp + 1)
        code = ''

        for x in range(0, 5 - len(rep)):
            code += '0'

        code += rep
        return code

    @api.model
    def _default_name(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'atm.work.order')])
        return sequence.get_next_char(sequence.number_next_actual)

    code = Char(required=True, default=_get_code, track_visibility='onchange')
    number = Char(track_visibility='onchange')

    opening_date = Date(readonly=False, track_visibility='onchange')
    closing_date = Date(readonly=False, track_visibility='onchange')

    execute_cost_center_id = Many2one('l10n_cu_base.cost_center', string='Execute', required=True, track_visibility='onchange')
    receive_cost_center_id = Many2one('l10n_cu_base.cost_center', string='Receive', required=True, track_visibility='onchange')
    state = Selection([('created', 'Created'), ('open', 'Opened'), ('closed', 'Closed'), ('cancel', 'Cancelada')], default='created', readonly=True, track_visibility='onchange')
    type_id = Many2one('atm.work_order.type', string='Type', required=True, readonly=False, track_visibility='onchange')

    creator_id = Many2one('hr.employee', string='Open', readonly=True, track_visibility='onchange')
    emitter_id = Many2one('hr.employee', string='Emmitter', required=True, track_visibility='onchange')
    executor_id = Many2one('hr.employee', string='Executor', required=True, track_visibility='onchange')
    shutter_id = Many2one('hr.employee', string='Shutter', readonly=True, track_visibility='onchange')

    realized_work = Char(track_visibility='onchange')
    equipment_or_area = Char(required=True, track_visibility='onchange')
    note = Text(track_visibility='onchange')
    description_cancel = Char('Motivo', track_visibility='onchange')
    user_cancel_id = Many2one('res.users', 'Usuario', track_visibility='onchange')
    date_cancel = Datetime('Fecha y Hora', track_visibility='onchange')

    product_order_ids = One2many('warehouse.product_order', inverse_name='work_order_id', string='Products...')

    work_order_mtto_id = Many2one('turei_maintenance.work_order', string='WOMTTO', required=False)
    name = Char('Número ID', default=_default_name)
    number_new = Char("Número Nuevo", default=_default_name)

    # @api.onchange('number')
    # def on_change_number(self):
    #     if self.number:
    #         first = str(self.number[0])
    #         second = str(self.number[1])
    #         code = ''
    #
    #         if first.isalpha():
    #             code += first
    #         if second.isalpha():
    #             code += second
    #
    #         types = self.env['atm.work_order.type'].search([('name', '=', code)])
    #         if types:
    #             self.type_id = types[0]

    def button_open(self):
        self.state = 'open'
        self.closing_date = None

        if not self.opening_date:
            self.opening_date = Date.today()
        self.product_order_maintenance()
        employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
        if len(employees):
            self.creator_id = employees[0].id

    def button_close(self):
        self.state = 'closed'
        self.closing_date = Date.today()
        self.product_order_maintenance()
        employees = self.env['hr.employee'].search([('user_id', '=', self._uid)])
        if len(employees):
            self.shutter_id = employees[0].id

    def button_cancel(self):
        if len(self.product_order_ids) > 0:
            raise ValidationError('No puede cancelar la Órden de Trabajo debido a que tiene productos asignados!')
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Asistente para cancelar Orden de Trabajo'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'atm.work_order_cancel_wizard',
                'target': 'new',
            }
            # self.state = 'cancel'



    # @api.one
    # @api.constrains('number')
    # def _check_number(self):
    #     value = ""
    #     for char in self.number:
    #         if not char.isalpha():
    #             value += char
    #
    #     work_orders = self.search([('number', 'ilike', value), ('id', '<>', self.id)])
    #
    #     for work_order in work_orders:
    #         to_compare = ''
    #         for char in work_order.number:
    #             if not char.isalpha():
    #                 to_compare += char
    #
    #         if value == to_compare:
    #             raise ValidationError(_('Another work order have the same number...'))
    #
    #     return True

    def product_order_maintenance(self):
        work_order = self.env['turei_maintenance.work_order'].browse(self.work_order_mtto_id.id)
        if work_order:
            work_order.product_order_ids.unlink()
            list_product = []
            for line in self.product_order_ids:
                list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
            work_order.write({'product_order_ids': list_product})

    @api.onchange('type_id')
    def _onchange_type_id(self):
        if self.type_id:
            self.number_new = self.type_id.name + self.name

    # @api.depends('type_id', 'name')
    # def _compute_number_new(self):
    #     for record in self:
    #         if record.name and record.type_id:
    #             record.number_new = record.type_id.name + record.name
    #         else:
    #             record.number_new = record.name

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('atm.work.order') or '/'
        vals['number_new'] = self.env['atm.work_order.type'].browse([vals['type_id']]).name + vals['name']
        work_order = super(WorkOrder, self).create(vals)
        if vals.get('type_id'):
            if work_order.type_id.name == 'A' or work_order.type_id.name == 'P':
                if vals.get('product_order_ids'):
                    list_product = []
                    for line in work_order.product_order_ids:
                        list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
                    vals['product_order_ids'] = list_product
                work_order_mtto = self.env['turei_maintenance.work_order'].sudo().create(vals)
                work_order.write({'work_order_mtto_id': work_order_mtto.id})
        return work_order

    @api.multi
    def write(self, vals):
        res = super(WorkOrder, self).write(vals)
        work_order = self.env['turei_maintenance.work_order'].browse(self.work_order_mtto_id.id)
        if work_order:
            work_order.product_order_ids.unlink()
            list_product = []
            for line in self.product_order_ids:
                list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))
            vals['product_order_ids'] = list_product
            work_order.write(vals)
        return res
WorkOrder()


class WorkOrderType(Model):
    _name = 'atm.work_order.type'
    _description = 'atm.work_order.type'

    name = Char()
    note = Text(string='Description')
    is_used_in_budget = Boolean('Used in budget?')
WorkOrderType()
