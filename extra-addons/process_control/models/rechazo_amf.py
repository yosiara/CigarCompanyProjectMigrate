# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RechazoAMF(models.Model):
    _name = 'process_control.rechazo_amf'
    _inherits = {"process_control.rechazo": "rechazo_id"}
    _description = "Rechazo AMF"

    rechazo_id = fields.Many2one(comodel_name='process_control.rechazo', string='Rechazo')

    prod_en_cajones = fields.Float('Producción en cajones *', required=True)
    rechazo_en_cajetillas = fields.Integer('Rechazo en cajetillas *', required=True)
    
    # @api.onchange("rechazo_id")
    # def _get_default_turn_attendance(self):
    #     if self.tecnolog_control_id.turn_id and self.tecnolog_control_id.session:
    #         domain = [('session', '=', self.tecnolog_control_id.session), ('turn_id', '=', self.tecnolog_control_id.turn_id.id)]
    #         rechazo_recs = self.tecnolog_control_id.rechazo_amf_ids.filtered_domain([('productive_line_id', '=', self.productive_line_id.id)]).sorted(key=lambda r: r.turn_attendance_id.hour_from, reverse=True) if self.productive_line_id else self.tecnolog_control_id.rechazo_amf_ids.sorted(key=lambda r: r.turn_attendance_id.hour_from, reverse=True)
    #         productive_line_recs = self.tecnolog_control_id.productive_section_id.productive_line_ids.sorted(key=lambda r: r.id)
    #         if productive_line_recs:
    #             self.productive_line_id = productive_line_recs[0].id
    #             machine_recs = productive_line_recs[0].machine_ids.filtered(lambda r: r.machine_type_id.name == 'AMF')
    #             if machine_recs:
    #                 self.machine_id = machine_recs[0].id
    #         turn_attendance_recs = self.turn_attendance_id.search(domain, order='hour_from asc', limit=1)
    #         next_turn_attendance = turn_attendance_recs.filtered_domain([('hour_from', '>', rechazo_recs[0].turn_attendance_id.hour_from)])
    #         if next_turn_attendance: # Next Hour
    #             self.turn_attendance_id = next_turn_attendance[0].id
    #         else: # Overtime
    #             overtime = turn_attendance_recs.filtered_domain([('hour_from', '=', 0), ('hour_to', '=', 0)])
    #             if overtime:
    #                 self.turn_attendance_id = overtime[0].id