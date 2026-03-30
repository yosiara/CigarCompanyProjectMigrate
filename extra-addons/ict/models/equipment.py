# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    computer_id = fields.One2many(comodel_name='ict.computer', inverse_name='equipment_id', string='ICT Computer')

    def action_view_ict_computer(self):
        """Acción para ver la computadora desde el equipo de mantenimiento"""
        self.ensure_one()
        if not self.computer_id:
            return {'type': 'ir.actions.act_window_close'}
        
        return {
            'type': 'ir.actions.act_window',
            'name': f'ICT Computer: {self.computer_id.name}',
            'res_model': 'ict.computer',
            'res_id': self.computer_id.id,
            'view_mode': 'form',
            'view_id': self.env.ref('ict.view_ict_computer_form').id,
            'target': 'current',
            'context': {'default_equipment_id': self.id}
        }