# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import time

class Turn(models.Model):
    _name = "process_control.turn"
    _description = "Turn"

    name = fields.Char(required=True, default="Turno ")
    turn_attendance_ids = fields.One2many('process_control.turn_attendance', inverse_name='turn_id', string='Tiempo de Trabajo')
    turn_attendance_context = fields.Binary(compute="_context_turn_attendance", exportable=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre del Turno debe ser único.'),
    ]

    def hour_range(self, session=False):
        self.ensure_one()
        minimo = 23.99
        maximo = 0.00
        domain = [('hour_from', '!=', 0.0), ('hour_to', '!=', 0.0)]
        if session:
            domain.append(('session', '=', session))
        for att in self.turn_attendance_ids.filtered_domain(domain):
            minimo = min(minimo, att.hour_from, att.hour_to)
            maximo = max(maximo, att.hour_from, att.hour_to)
        return (minimo, maximo)

    def float_to_time(self, h):
        if h >= 24.0:
            return time(23, 59, 59, 999999)
        if h <= 0.0:
            return time(0, 0, 0, 0)
        hours = int(h)
        minutes = int(round((h - hours) * 60))
        return time(hours, minutes)

    @api.depends("turn_attendance_ids")
    def _context_turn_attendance(self):
        for rec in self:
            name = "(7:00-8:00)"
            session = "morning"
            hour_from = 7.0
            hour_to = 8.0
            att_recs = rec.turn_attendance_ids.sorted(key=lambda r: r.hour_to, reverse=True)
            if att_recs:
                session = att_recs[0].session
                hour_from = att_recs[0].hour_to
                hour_to = hour_from + 1
                name = f"({self.float_to_time(hour_from).strftime('%H:%M')}-{self.float_to_time(hour_to).strftime('%H:%M')})"
            rec.turn_attendance_context = {
                "default_session": session,
                "default_hour_from": hour_from,
                "default_hour_to": hour_to,
                "default_name": name,
            }