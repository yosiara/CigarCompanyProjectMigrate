# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class rechazo_modulo1(models.Model):
    _name = 'process_control.rechazo_mod1'
    _inherits = {"process_control.rechazo_amf": "rechazo_amf_id"}

    rechazo_amf_id = fields.Many2one(
        comodel_name='process_control.rechazo_amf',
        string='Rechazo AMF', required=True, readonly=True, ondelete='cascade',
    )
    #productive_line_id = fields.Many2one('process_control.productive_section_lines', string='Líneas Productivas')
    #machine_id = fields.Many2one('process_control.machine', 'Máquina',
    #                             # dominio vacio hasta que se escoja una seccion productiva
    #                            domain=[('id', 'in', [])])
    # machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina',
    #                                   related='machine_id.machine_type_id')

    # machine_type_name = fields.Char("Machine Type name", related='machine_type_id.name')
    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )

    # rechazo_en_cajetillas = fields.Integer('Rechazo en cajetillas')
    rechazo_en_cigarrillos = fields.Integer('Rechazo en cigarrillos')
    # produccion_en_cajones = fields.Float('Produción en cajetillas')
    produccion_en_cigarrillos = fields.Integer('Produción en cigarrillos')

    _sql_constraints = [('rechazo_amf_id_uniq', 'unique(rechazo_amf_id)', "Este existe un rechazo igual")]
    # tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control",
    #                                       string="Modelo Control", ondelete='cascade',
    #                                       required=True, )

    # tec_model_type = fields.Selection(string="Documento/control",
    #                                   selection=[('mod1', 'Módulo')], required=True, readonly=True, default='mod1')

    # @api.model_create_multi
    # @api.onchange('productive_line_id')
    # def _onchange_productive_line(self):
    #     for psc in self.productive_line_id:
    #             return {'domain': {'machine_id': [('id', 'in', psc.productive_line.machine_ids.ids),
    #                                               ('machine_type_id.name', 'in', ['NANO', 'SBO', 'SRC'])]}}
    #     return {'domain': {'machine_id': [('id', 'in', [])]}}

    # @api.onchange('machine_id')
    # def _onchange_machine_id(self):
    #     if self.productive_line_id:
    #         return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids),
    #                                               ('machine_type_id.name', 'in', ['NANO', 'SBO', 'SRC'])]}}