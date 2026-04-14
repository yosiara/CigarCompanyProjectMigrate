# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class Machine(models.Model):
    _name = "turei_process_control.machine"
    _description = tools.ustr("Máquinas")

    def _get_default_name(self):
        if self.machine_type_id:
            return str(self.machine_type_id.name) + '-Mod'
        return 'Tipo-Mod-línea'

    name = fields.Char('Nombre', size=40, required=True, copy=False, default=_get_default_name)
    machine_type_id = fields.Many2one('turei_process_control.machine_type', string='Tipo de máquina')
    productive_section_id = fields.Many2one('turei_process_control.productive_section', string='Sección productiva')
    set_of_peaces = fields.Many2many('turei_process_control.machine_set_of_peaces_nomenclature',
                                     relation="turei_process_control_peaces_machine", copy=True,
                                     column1='peaces_id', column2='machine_id', string='Subconjuntos de piezas')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la máquina debe ser único.'),
    ]


    @api.onchange('machine_type_id')
    def chancge_machine_type(self):
        if self.machine_type_id:
            sets = self.env['turei_process_control.machine_set_of_peaces_nomenclature'].search(
                [('machine_type_id.id', '=', self.machine_type_id.id)])
            self.set_of_peaces = sets


class SetOfPeacesNomenclature(models.Model):
    _name = "turei_process_control.machine_set_of_peaces_nomenclature"
    _rec_name = "name"
    _description = "Nombres de conjunto de piezas"

    name = fields.Char('Nombre del conjunto', size=40, required=True)
    machine_type_id = fields.Many2one('turei_process_control.machine_type', string='Tipo de máquina')
