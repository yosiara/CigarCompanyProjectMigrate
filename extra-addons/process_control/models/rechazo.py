# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Rechazo(models.Model):
    _name = "process_control.rechazo"
    _description = "Rechazo"

    turn_attendance_id = fields.Many2one('process_control.turn_attendance', string="Hora *", required=True)

    productive_line_id = fields.Many2one('process_control.productive_line', string='Líneas Prod. *', required=True)
    machine_id = fields.Many2one('process_control.machine', string='Máquina *', required=True)
    
    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control", ondelete='cascade', required=True)

    # @api.model
    # def default_get(self, fields):
    #     res = super(Rechazo, self).default_get(fields)
    #     rec_last = self.search([], order='id desc', limit=1)
    #     if rec_last:
    #         res["productive_line_id"] = rec_last.productive_line_id.id
    #         res["machine_id"] = rec_last.machine_id.id
    #     return res

    # @api.depends("tecnolog_control_id.turproduccion_en_cajonesn_attendance_id")
    # def _compute_hours(self):
    #     if self.tecnolog_control_id.turn_attendance_id:
    #         hours_array = []
    #         hour_from = self.tecnolog_control_id.turn_attendance_id.hour_from
    #         hour_to = self.tecnolog_control_id.turn_attendance_id.hour_to
    #         while hour_from < hour_to:
    #             hours_array.append((f"{hour_from}-{hour_from+1}", f"{hour_from}-{hour_from+1}"))
    #             hour_from += 1
    #         hours_array.append(("extra_hours", "Extra Hours"))
    #         self.hour = hours_array
    #     else:
    #         self.hour = [()]
