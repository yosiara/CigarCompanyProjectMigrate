# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class Machine(models.Model):
    _name = 'process_control.machine'
    _description = 'Machine'

    name = fields.Char('Name *', required=True)
    machine_type_id = fields.Many2one('process_control.machine_type', string='Machine Type *', required=True)
    productive_section_id = fields.Many2one('process_control.productive_section', string='Productive Section *', required=True)
    productive_line_id = fields.Many2one('process_control.productive_line', string='Productive Line')
    line_domain = fields.Binary(compute='_get_line_domain', exportable=False)
    set_of_peaces = fields.Many2many(
        comodel_name='process_control.machine_set_of_peaces', 
        relation='process_control_machine_machine_set_of_peaces_asoc', 
        column1='machine_id', 
        column2='machine_set_of_peaces_id',
        ondelete='restrict',
        required=True, 
        string='Type of Peaces *',
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The machine name must be unique!'),
    ]

    @api.constrains('productive_line_id', 'productive_section_id', 'machine_type_id')
    def _constrains_lines(self):
        if self.productive_line_id:
            match = self.search([
                ('productive_line_id', '=', self.productive_line_id.id), 
                ('productive_section_id', '!=', self.productive_section_id.id)
            ], limit=1)
            if match:
                raise ValidationError(
                    _('The production line %s can only contain machines from its associated module.') % (
                        self.productive_line_id.name
                    )
                )

            match = self.search([
                ('id', '!=', self.id), 
                ('productive_line_id', '=', self.productive_line_id.id), 
                ('machine_type_id', '=', self.machine_type_id.id), 
                ('productive_section_id', '=', self.productive_section_id.id)
            ], limit=1)
            if match:
                raise ValidationError(
                    _('The line %s already has a machine of type %s associated with it.') % (
                        self.productive_line_id.name,
                        match.machine_type_id.name
                    )
                )

    @api.onchange('machine_type_id')
    def _onchange_machine_type_id(self):
        if self.machine_type_id:
            self.set_of_peaces = self.set_of_peaces.search([('machine_type_ids', '=', self.machine_type_id.id)])

    @api.depends('productive_section_id')
    def _get_line_domain(self):
        for rec in self:
            if rec.productive_section_id:
                rec.line_domain = [('productive_section_id', '=', rec.productive_section_id.id)]
            else:
                rec.line_domain = [('id', 'in', [])]

