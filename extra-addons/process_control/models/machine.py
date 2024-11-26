# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError


class Machine(models.Model):
    _name = "process_control.machine"
    _description = "Máquinas"

    # def _get_default_name(self):
    #     if self.machine_type_id:
    #         return str(self.machine_type_id.name) + '-Mod-Line'

    name = fields.Char('Nombre *', size=40, copy=False, required=True)
    machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina *', required=True)
    productive_section_id = fields.Many2one('process_control.productive_section', string='Módulo *', required=True)
    productive_line_id = fields.Many2one('process_control.productive_line', string='Productive Line')
    set_of_peaces = fields.Many2many('process_control.machine_set_of_peaces',
                            relation="process_control_machine_machine_set_of_peaces_asoc", copy=True, required=True, ondelete='restrict',
                            column1='machine_id', column2='machine_set_of_peaces_id', string='Subconjuntos de piezas *')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
        'El nombre de la máquina debe ser único.'),
    ]

    @api.constrains("productive_line_id","productive_section_id","machine_type_id")
    def _constrains_lines(self):
        if self.productive_line_id:
            match = self.search([("productive_line_id", "=", self.productive_line_id.id), ("productive_section_id", "!=", self.productive_section_id.id)], limit=1)
            if match:
                raise ValidationError(_(f"La línea {self.productive_line_id.name} ha sido asociada al módulo {match.productive_section_id.name}, por lo tanto solo puede contener máquinas de dicho módulo"))

            match = self.search([("id", "!=", self.id),("productive_line_id", "=", self.productive_line_id.id), ("machine_type_id", "=", self.machine_type_id.id), ("productive_section_id", "=", self.productive_section_id.id)], limit=1)
            if match:
                raise ValidationError(_(f"La línea {self.productive_line_id.name} ya tiene asociada una máquina del tipo {match.machine_type_id.name}"))

    @api.onchange('machine_type_id')
    def _onchange_machine_type_id(self):
        if self.machine_type_id:
            self.set_of_peaces = self.set_of_peaces.search([('machine_type_ids', '=', self.machine_type_id.id)])


    # @api.model_create_multi
    # def create(self, vals_list):
    #     machines = super().create(vals_list)
    #     match = []
    #     for vals in machines:
    #         vals.name = vals.machine_type_id.name + '-' + vals.productive_section_id.name
    #         if vals.name not in match:
    #             match.append(vals.name)
    #         else:
    #             raise ValidationError
    #     return machines

    # def write(self, vals):
    #     res = super().write(vals)
    #     if "productive_section_id" in vals or "machine_type_id" in vals:
    #         self.name = self.machine_type_id.name + '-' + self.productive_section_id.name
    #     return res
