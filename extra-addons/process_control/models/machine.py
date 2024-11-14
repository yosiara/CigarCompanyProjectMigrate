# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class Machine(models.Model):
    _name = "process_control.machine"
    _description = "Máquinas"

    # def _get_default_name(self):
    #     if self.machine_type_id:
    #         return str(self.machine_type_id.name) + '-Mod-Line'

    name = fields.Char('Nombre', size=40, copy=False)
    machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina', required=True)
    productive_section_id = fields.Many2one('process_control.productive_section', string='Módulo', required=True)
    set_of_peaces = fields.Many2many('process_control.machine_set_of_peaces_nomenclature',
                                     relation="process_control_peaces_machine", copy=True, required=True,
                                     column1='peaces_id', column2='machine_id', string='Subconjuntos de piezas')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la máquina debe ser único.'),
    ]

    @api.onchange('machine_type_id')
    def _onchange_machine_type_id(self):
        if self.machine_type_id:
            sets = self.env['process_control.machine_set_of_peaces_nomenclature'].search(
                [('machine_type_id.id', '=', self.machine_type_id.id)])
            self.set_of_peaces = sets

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = super().create(vals_list)
        for vals in vals_list:
            if not vals.name:
                #machine = vals.get("machine_type_id")
                vals.name = vals.machine_type_id.name + '-' + vals.productive_section_id.name
        return vals_list
