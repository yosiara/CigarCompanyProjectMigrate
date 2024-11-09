# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class Interruption(models.Model):
    _name = "turei_process_control.interruption"
    _description = "Interruption"
    _rec_name = 'name'

    name = fields.Char(string="Nombre", required=False, compute='_calc_name')
    interruption_type = fields.Many2one('turei_process_control.interruption.type', 'Tipo', required=True)
    machine_id = fields.Many2one('turei_process_control.machine', 'Máquina',
                                 # dominio vacio hasta que se escoja una seccion productiva
                                 domain=[('id', 'in', [])])
    set_of_peaces_id = fields.Many2one(comodel_name="turei_process_control.machine_set_of_peaces_nomenclature",
                                       string="Subconjunto", domain=[('id', 'in', [])],
                                       required=False, )
    time = fields.Integer('Tiempo en minutos', required=True)
    frequency = fields.Integer('Frecuencia', required=True)
    # modelo del control del proceso, recoge todas las interrupciones de un turno en un dia X
    tec_control_model = fields.Many2one(comodel_name="turei_process_control.tecnolog_control_model", string="Documento",
                                        required=False, )
    productive_line_id = fields.Many2one('turei_process_control.productive_section_lines', string='Líneas Productivas')

    @api.onchange('productive_line_id')
    def _onchange_productive_line(self):
        self.machine_id = False
        if self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids)]}}
        self._cr.execute("SELECT machine_id FROM turei_process_control_produc_line_machine_asoc")
        machines_in_line = self._cr.fetchall()
        return {'domain': {'machine_id': [('id', 'not in', machines_in_line),('productive_section_id', '=',  self.tec_control_model.productive_section.id)]}}

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        domain_interruption = self.get_domain_interruption_type()
        if self.machine_id:
            machine_types = self.env['turei_process_control.machine_set_of_peaces_nomenclature'].search(
                [('machine_type_id', '=', self.machine_id.machine_type_id.id)])
            return {'domain': {'set_of_peaces_id': [('id', 'in', machine_types.ids)],
                               'interruption_type': domain_interruption}}
        return {'domain': {'set_of_peaces_id': [('id', 'in', [])], 'interruption_type': domain_interruption}}

    @api.onchange('interruption_type')
    def _onchange_interruption_type(self):
        domain_interruption = self.get_domain_interruption_type()
        if not self.machine_id:
            return {'domain': {'interruption_type': domain_interruption}}
        else:
            return {'domain': {'interruption_type': domain_interruption}}

    def get_domain_interruption_type(self):
        if not self.machine_id:
            interruption_types = self.env['turei_process_control.interruption.type'].search(
                [('is_linked_to_machine', '=', False)])
            return [('id', 'in', interruption_types.ids)]
        else:
            interruption_types_ids = []
            interruption_types = self.env['turei_process_control.interruption.type'].search([
                '|', ('is_linked_to_machine', '=', True), ('use_in_any_machine', '=', True)
            ])
            for interruption_type in interruption_types:
                aux_type = interruption_type.machines_related.search_count(
                    [('id', '=', self.machine_id.machine_type_id.id)])
                if aux_type > 0:
                    interruption_types_ids.append(interruption_type.id)

            return [('id', 'in', interruption_types_ids)]

    @api.multi
    @api.depends('interruption_type', 'machine_id')
    def _calc_name(self):
        for intp in self:
            if intp.interruption_type.name and intp.machine_id.name:
                intp.name = tools.ustr(intp.interruption_type.name) + '-' + tools.ustr(intp.machine_id.name)
            elif intp.interruption_type.name and not intp.machine_id.name:
                intp.name = tools.ustr(intp.interruption_type.name)
            elif not intp.interruption_type.name and intp.machine_id.name:
                intp.name = tools.ustr(intp.machine_id.name)

    @api.multi
    @api.constrains('time')
    def check_time(self):
        for inter in self:
            if inter.time == 0.00:
                raise ValidationError(
                    tools.ustr("Interruptión de tipo ") + tools.ustr(inter.name) + tools.ustr(
                        " no puede tener tiempo 0"))
