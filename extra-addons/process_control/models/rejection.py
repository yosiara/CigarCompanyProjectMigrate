# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Rejection(models.Model):
    _name = 'process_control.rejection'
    _description = 'Rejection'

    productive_line_id = fields.Many2one('process_control.productive_line', string='Productive Line *', required=True)
    line_domain = fields.Binary(compute='_get_line_domain', exportable=False)

    machine_id = fields.Many2one('process_control.machine', string='Machine *', required=True)
    machine_domain = fields.Binary(compute='_get_machine_domain', exportable=False)
    
    tecnolog_control_id = fields.Many2one(comodel_name='process_control.tecnolog_control', ondelete='cascade', required=True)

    @api.depends('tecnolog_control_id', 'productive_line_id')
    def _get_machine_domain(self):
        for rec in self:
            if rec.productive_line_id:
                rec.machine_domain = [('productive_line_id', '=', rec.productive_line_id.id)]
            elif rec.tecnolog_control_id.productive_section_id:
                rec.machine_domain = [('productive_section_id', '=', rec.tecnolog_control_id.productive_section_id.id), ('productive_line_id', '=', False)]
            else:
                rec.machine_domain = [('id', 'in', [])]

    @api.depends('tecnolog_control_id')
    def _get_line_domain(self):
        for rec in self:
            if rec.tecnolog_control_id.productive_section_id:
                rec.line_domain = [('productive_section_id', '=', rec.tecnolog_control_id.productive_section_id.id)]
            else:
                rec.line_domain = [('id', 'in', [])]
