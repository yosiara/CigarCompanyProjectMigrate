# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class RechazoAmf(models.Model):
    _name = 'process_control.rechazo_amf'

    productive_line_id = fields.Many2one('process_control.productive_section_lines', string='Líneas Productivas')
    machine_id = fields.Many2one('process_control.machine', 'Máquina',
                                 # dominio vacio hasta que se escoja una seccion productiva
                                 domain=[('id', 'in', [])])
    machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina',
                                      related='machine_id.machine_type_id')

    rechazo_en_cajetillas = fields.Integer('Rechazo en cajetillas')
    produccion_en_cajones = fields.Float('Produción en cajones')
    # tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control",
    #                                       string="Modelo Control", ondelete='cascade',
    #                                       required=True, )
    tec_model_type = fields.Selection(string="Documento/control",
                                      selection=[('mod', 'Módulo')], readonly=True, default='mod')

    rechazo_mod1_ids = fields.One2many(comodel_name="process_control.rechazo_mod1",
        inverse_name="rechazo_amf_id",
        string="Rechazo 'NANO', 'SBO', 'SRC'", required=False)

    @api.model_create_multi
    @api.onchange('productive_line_id')
    def _onchange_productive_line(self):
        for psc in self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', psc.productive_line.machine_ids.ids),
                                              ('machine_type_id.name', '=', 'AMF')]}}
        return {'domain': {'machine_id': [('id', 'in', [])]}}

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids),
                                              ('machine_type_id.name', '=', 'AMF')]}}
