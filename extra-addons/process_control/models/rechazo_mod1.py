# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class RechazoMod1(models.Model):
    _name = 'process_control.rechazo_mod1'
    _inherits = {"process_control.rechazo": "rechazo_id"}
    _description = "Rechazo Módulo 1"

    rechazo_id = fields.Many2one(comodel_name='process_control.rechazo', string='Rechazo')
    
    prod_en_cigarrillos = fields.Integer('Produción en cigarrillos *', required=True)
    rechazo_en_cigarrillos = fields.Integer('Rechazo en cigarrillos *', required=True)
    #prod_en_cajetillas = fields.Integer('Producción en cajetillas')
    
    _sql_constraints = [
        ('rechazo_amf_id_uniq', 'unique(rechazo_amf_id)', "Existe un rechazo igual"),
    ]

    # @api.onchange("rechazo_id")
    # def _get_default_turn_attendance(self):
    #     if self.tecnolog_control_id.turn_id and self.tecnolog_control_id.session:
    #         domain = [('session', '=', self.tecnolog_control_id.session), ('turn_id', '=', self.tecnolog_control_id.turn_id.id)]
    #         rechazo_recs = self.tecnolog_control_id.rechazo_mod1_ids.sorted(key=lambda r: r.turn_attendance_id.hour_from, reverse=True)
    #         next_turn_attendance = self.turn_attendance_id.search(domain + [('hour_from', '>', rechazo_recs[0].turn_attendance_id.hour_from)], order='hour_from asc', limit=1)
    #         if next_turn_attendance: # Next Hour
    #             self.turn_attendance_id = next_turn_attendance.id
    #         else: # Overtime
    #             overtime = self.turn_attendance_id.search(domain + [('hour_from', '=', 0), ('hour_to', '=', 0)], order='hour_from asc', limit=1)
    #             if overtime:
    #                 self.turn_attendance_id = overtime.id

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