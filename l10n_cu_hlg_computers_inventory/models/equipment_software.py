# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class EquipmentSoftware(models.Model):
    _name = 'equipment.software'
    _description = 'equipment.software'

    name = fields.Char('Name', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', ondelete='cascade')
    publisher = fields.Char()
    version = fields.Char()
    ocs_external_id = fields.Integer()
    notes = fields.Text()

    #@api.multi
    def write(self, vals):
        vals['ocs_external_id'] = False
        res = super(EquipmentSoftware, self).write(vals)
        return res

    #@api.one
    def confirm(self):
        self.ocs_external_id = False
        return True
