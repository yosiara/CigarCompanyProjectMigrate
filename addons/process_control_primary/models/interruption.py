# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class Interruption(models.Model):
    _name = "process_control_primary.interruption"
    _description = "Interruption"
    _rec_name = 'name'

    name = fields.Char(string="Nombre", required=False, compute='_calc_name')
    interruption_type = fields.Many2one('process_control_primary.interruption.type', 'Tipo', required=True)


    machine_type_id = fields.Many2one('process_control_primary.machine_type', string='Máquina', )

    time = fields.Integer('Tiempo en minutos', required=True)
    frequency = fields.Integer('Frecuencia', required=True)
    # modelo del control del proceso, recoge todas las interrupciones de un turno en un dia X
    tec_control_model = fields.Many2one(comodel_name="process_control_primary.tecnolog_control_model", string="Documento",
                                        required=False, )
    productive_line_id = fields.Many2one('process_control_primary.productive_line', string='Líneas Productivas')


    @api.onchange('productive_line_id')
    def _onchange_productive_line(self):
        self.machine_type_id = False
        self.interruption_type = False
        if self.productive_line_id:
            return {'domain': {'machine_type_id': [('id', 'in', self.productive_line_id.machine_type_ids.ids)]}}

    @api.onchange('machine_type_id')
    def _onchange_machine_type_id(self):
        self.interruption_type = False
        if self.machine_type_id:
            interruption_types = self.env['process_control_primary.interruption.type'].search(['|',('is_linked_to_machine', '=', True),('use_in_any', '=', True)])
            return {'domain': {'interruption_type': [('id', 'in', interruption_types.ids)]}}
        else:
            interruption_types = self.env['process_control_primary.interruption.type'].search([('is_linked_to_machine', '=', False)])
            return {'domain': {'interruption_type': [('id', 'in', interruption_types.ids)]}}


    @api.multi
    @api.depends('interruption_type', 'machine_type_id')
    def _calc_name(self):
        for intp in self:
            if intp.interruption_type.name and intp.machine_type_id.name:
                intp.name = tools.ustr(intp.interruption_type.name) + '-' + tools.ustr(intp.machine_type_id.name)
            elif intp.interruption_type.name and not intp.machine_type_id.name:
                intp.name = tools.ustr(intp.interruption_type.name)
            elif not intp.interruption_type.name and intp.machine_type_id.name:
                intp.name = tools.ustr(intp.machine_type_id.name)

    @api.multi
    @api.constrains('time')
    def check_time(self):
        for inter in self:
            if inter.time == 0.00:
                raise ValidationError(
                    tools.ustr("Interruptión de tipo ") + tools.ustr(inter.name) + tools.ustr(
                        " no puede tener tiempo 0"))

