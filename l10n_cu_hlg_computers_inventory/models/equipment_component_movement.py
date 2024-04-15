# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class ComponentMovement(models.Model):
    _name = 'equipment.component_movement'
    _description = 'equipment.component_movement'
    _order = 'datetime desc'

    datetime = fields.Datetime('Date')
    equipment_id = fields.Many2one(comodel_name='maintenance.equipment', string='Equipment', ondelete='cascade')
    component_id = fields.Many2one('equipment.component', string='Component', ondelete='cascade')
    component_type = fields.Char(string='Component type', compute='_compute_component_type', store=True)
    type = fields.Selection([('down', 'Down'), ('up', 'Up')])
    # new_seal = fields.Char('New Seal')

    state = fields.Selection(
        [('waiting_approval', 'Waiting for approval'), ('approved', 'Approved')], 'Status', readonly=True,
        track_visibility='onchange', copy=False, default='waiting_approval'
    )

    #@api.one
    @api.depends('component_id')
    def _compute_component_type(self):
        if self.equipment_id and self.component_id:
            self.component_type = self.component_id.component_type

    #@api.one
    def action_approve(self):
        self.equipment_id.quantity_movements_for_approval = self.equipment_id.quantity_movements_for_approval - 1
        self.state = 'approved'


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    has_movements_for_approval = fields.Boolean(compute='_compute_has_movements_for_approval')
    quantity_movements = fields.Integer(compute='_compute_quantity_movements')
    quantity_movements_for_approval = fields.Integer()

    movement_ids = fields.One2many(
        'equipment.component_movement', inverse_name='equipment_id', string='Movements',
        domain=[('state', '=', 'approved')]
    )

    movement_for_approval_ids = fields.One2many(
        'equipment.component_movement', inverse_name='equipment_id', string='Movements',
        domain=[('state', '=', 'waiting_approval')]
    )

    #@api.one
    def _compute_has_movements_for_approval(self):
        args = [('equipment_id', '=', self.id), ('state', '=', 'waiting_approval')]
        if len(self.env['equipment.component_movement'].search(args)):
            self.has_movements_for_approval = True

    #@api.multi
    def show_movements(self):
        return {
            'name': _('Detailed view...'),
            'type': 'ir.actions.act_window',
            'res_model': 'equipment.component_movement',
            'domain': "[('equipment_id', '=', " + str(self.id) + "), ('state', '=', 'waiting_approval')]",
            'context': "{}",
            'view_mode': 'tree',
            'target': 'current',
        }

    #@api.one
    def _compute_quantity_movements(self):
        self.quantity_movements = len(self.movement_ids)

    #@api.one
    def approve_all_movements(self):
        self.quantity_movements_for_approval = 0
        self.env['equipment.component_movement'].search(
            [('equipment_id', '=', self.id), ('state', '=', 'waiting_approval')]
        ).write({'state': 'approved'})
        return True
