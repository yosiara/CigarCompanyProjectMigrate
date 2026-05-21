# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.translate import _


class ICTComputerApplication(models.Model):
    _name = 'ict.computer.application'
    _description = 'ICT Computer Application'

    name = fields.Char('Name', required=True)
    computer_id = fields.Many2one('ict.computer', 'Computer', ondelete='cascade', index=True)
    publisher = fields.Char()
    version = fields.Char()
    ocs_external_id = fields.Integer()
    notes = fields.Text()

    # @api.multi
    # def write(self, vals):
    #     vals['ocs_external_id'] = False
    #     res = super(EquipmentApplication, self).write(vals)
    #     return res

    # @api.one
    # def confirm(self):
    #     self.ocs_external_id = False
    #     return True
