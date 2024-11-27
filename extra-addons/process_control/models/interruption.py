# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError

class Interruption(models.Model):
    _name = "process_control.interruption"
    _description = "Interruption"
    _rec_name = 'name'

    name = fields.Char(string="Nombre", required=False)
    interruption_type = fields.Many2one('process_control.interruption_type', 'Tipo *', required=True)
    machine_id = fields.Many2one('process_control.machine', 'Máquina')
    machine_domain = fields.Binary(compute="_get_machine_domain", exportable=False)
    set_of_peaces_id = fields.Many2one("process_control.machine_set_of_peaces", string="Subconjunto", required=False)
    peaces_domain = fields.Binary(compute="_get_peaces_domain", exportable=False)

    start_date = fields.Float(string="Inicio *", required=True)
    end_date = fields.Float(string="Fin *", required=True)
    
    #time = fields.Integer('Tiempo en minutos', required=True)
    #frequency = fields.Integer('Frecuencia', required=True)
    # modelo del control del proceso, recoge todas las interrupciones de un turno en un dia X
    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control", string="Documento", required=False)
    productive_line_id = fields.Many2one('process_control.productive_line', string='Líneas Prod.')
    line_domain = fields.Binary(compute="_get_line_domain", exportable=False)
    # productive_line_mia_id = fields.Many2one('process_control.productive_line', string='Líneas Prod.')

    # @api.onchange('productive_line_id')
    # def _onchange_productive_line(self):
    #     self.machine_id = False
    #     if self.productive_line_id:
    #         return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids)]}}
    #     self._cr.execute("SELECT machine_id FROM process_control_productive_line_machine_asoc")
    #     machines_in_line = self._cr.fetchall()
    #     return {'domain': {'machine_id': [('id', 'not in', machines_in_line),('productive_section_id', '=',  self.tecnolog_control_id.productive_section_id.id)]}}

    # @api.onchange('machine_id')
    # def _onchange_machine_id(self):
    #     domain_interruption = self.get_domain_interruption_type()
    #     if self.machine_id:
    #         machine_types = self.env['process_control.machine_set_of_peaces'].search(
    #             [('machine_type_id', '=', self.machine_id.machine_type_id.id)])
    #         return {'domain': {'set_of_peaces_id': [('id', 'in', machine_types.ids)],
    #                            'interruption_type': domain_interruption}}
    #     return {'domain': {'set_of_peaces_id': [('id', 'in', [])], 'interruption_type': domain_interruption}}

    # @api.onchange('interruption_type')
    # def _onchange_interruption_type(self):
    #     domain_interruption = self.get_domain_interruption_type()
    #     if not self.machine_id:
    #         return {'domain': {'interruption_type': domain_interruption}}
    #     else:
    #         return {'domain': {'interruption_type': domain_interruption}}

    # def get_domain_interruption_type(self):
    #     if not self.machine_id:
    #         interruption_types = self.env['process_control.interruption_type'].search([('is_linked_to_machine', '=', False)])
    #         return [('id', 'in', interruption_types.ids)]
    #     else:
    #         interruption_types_ids = []
    #         interruption_types = self.env['process_control.interruption_type'].search([
    #             '|', ('is_linked_to_machine', '=', True), ('use_in_any_machine', '=', True)
    #         ])
    #         for interruption_type in interruption_types:
    #             aux_type = interruption_type.machines_related.search_count(
    #                 [('id', '=', self.machine_id.machine_type_id.id)])
    #             if aux_type > 0:
    #                 interruption_types_ids.append(interruption_type.id)

    #         return [('id', 'in', interruption_types_ids)]

    # @api.model_create_multi
    # @api.depends('interruption_type', 'machine_id')
    # def _calc_name(self):
    #     for intp in self:
    #         if intp.interruption_type.name and intp.machine_id.name:
    #             intp.name = tools.ustr(intp.interruption_type.name) + '-' + tools.ustr(intp.machine_id.name)
    #         elif intp.interruption_type.name and not intp.machine_id.name:
    #             intp.name = tools.ustr(intp.interruption_type.name)
    #         elif not intp.interruption_type.name and intp.machine_id.name:
    #             intp.name = tools.ustr(intp.machine_id.name)

    # @api.model_create_multi
    # @api.constrains('time')
    # def check_time(self):
    #     for inter in self:
    #         if inter.time == 0.00:
    #             raise ValidationError(
    #                 tools.ustr("Interruptión de tipo ") + tools.ustr(inter.name) + tools.ustr(
    #                     " no puede tener tiempo 0"))

    @api.depends("tecnolog_control_id.productive_section_id", "productive_line_id")
    def _get_machine_domain(self):
        domain = []
        self.machine_id = False
        if self.tecnolog_control_id.productive_section_id:
            machine_in_section = self.machine_id.search([("productive_section_id", "=", self.tecnolog_control_id.productive_section_id.id)])
            domain.append(("id", "in", machine_in_section.ids))
            if self.productive_line_id:
                domain.append(('productive_line_id', '=', self.productive_line_id.id))
            self.machine_domain = domain
        else:
            domain.append(('id', 'in', False))
            self.machine_domain = domain

    @api.depends("machine_id")
    def _get_peaces_domain(self):
        self.set_of_peaces_id = False
        self.peaces_domain = [('id', 'in', self.machine_id.set_of_peaces.ids)] if self.machine_id else [('id', 'in', False)]

    @api.depends("tecnolog_control_id.productive_section_id")
    def _get_line_domain(self):
        self.productive_line_id = False
        if self.tecnolog_control_id.productive_section_id:
            machine_in_section = self.machine_id.search([("productive_section_id", "=", self.tecnolog_control_id.productive_section_id.id)])
            self.line_domain = [("id", "in", [rec.productive_line_id.id for rec in machine_in_section])]
        else:
            self.line_domain = [("id", "in", False)]
