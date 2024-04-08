# -*- coding: utf-8 -*-

from odoo import fields, models, api


class WorkOrderLine(models.Model):
    _name = 'computers_inventory.work_order_line'
    _description = 'WorkOrderLine'

    work_order_id = fields.Many2one(
        comodel_name='computers_inventory.work_order',
        string='work_order_id',
        required=True)

    start_date = fields.Date(string='Start Date', required=True)
    realized_work = fields.Char("Realized Work")
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment', domain="[('is_a_computer', '=', True)]")
    duration = fields.Char('Time')
    observations = fields.Text('Observations')


class WorkOrderComponentLine(models.Model):
    _name = 'computers_inventory.work_order_comp_line'
    _description = 'WorkOrderComponentLine'

    work_order_id = fields.Many2one(
        comodel_name='computers_inventory.work_order',
        string='work_order_id',
        required=True)

    equipment_id = fields.Many2one('maintenance.equipment', required=True, string='Equipment', domain="[('is_a_computer', '=', True)]")
    component_id = fields.Many2one('equipment.component', string='Component')
    component_type = fields.Selection(string='Component type', related='component_id.component_type', readonly=True)
    type = fields.Selection([('down', 'Down'), ('up', 'Up')])

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id:
            return {'domain': {'component_id': [('equipment_id', '=', self.equipment_id.id)]}}


class WorkOrder (models.Model):
    _name = 'computers_inventory.work_order'
    _description = 'Computers Inventory Work Order'
    _rec_name = 'number'

    number = fields.Char('Number', required=True)
    state = fields.Selection([('open', 'Open'), ('closed', 'Closed')], 'State', required=True, default='open')
    request_date = fields.Date(string='Request Date', required=True)
    close_date = fields.Date(string='Close Date')
    executor = fields.Many2one('hr.employee', string='Executor')
    responsible = fields.Many2one('hr.employee', string='Responsible')
    equipment_ready = fields.Boolean(string='Equipment Ready to work?', default=False)
    description = fields.Text('Description')
    line_ids = fields.One2many('computers_inventory.work_order_line', 'work_order_id', 'Realized Work')
    component_line_ids = fields.One2many('computers_inventory.work_order_comp_line', 'work_order_id', 'Changes in components')
    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request')



    


