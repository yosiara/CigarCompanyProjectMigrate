# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class TurnAttendance(models.Model):
    _name = "process_control.turn_attendance"
    _description = "Turn Attendance"

    name = fields.Char(string="Nombre *", required=True)
    hour_from = fields.Float(string='Hora de Inicio *', required=True)
    hour_to = fields.Float(string='Hora de Fin *', required=True,
        help="End of working.\nA specific value of 24:00 is interpreted as 23:59:59.999999.")
    turn_id = fields.Many2one("process_control.turn", string="Turno *", required=True, ondelete="cascade")

    production_by_hours_ids = fields.One2many('process_control.production_by_hours', 'turn_att_id', string='Production BY Hours')
    
    session = fields.Selection([
        ('morning', 'Mañana'),
        ('afternoon', 'Tarde'),
    ], string="Sesión *", required=True)

    @api.constrains("hour_from", "hour_to", "turn_id")
    def _constrains_hours(self):
        for rec in self:
            att_ids = rec.turn_id.turn_attendance_ids.sorted(key=lambda r: r.hour_from)
            after_midnight_recs = rec.turn_id.turn_attendance_ids.filtered(lambda r: r.hour_from > r.hour_to)
            if len(after_midnight_recs) == 1:
                maximo = after_midnight_recs[0].hour_from
                minimo = after_midnight_recs[0].hour_to
                if att_ids[0].hour_from < minimo or att_ids[len(att_ids)-1].hour_to > maximo:
                    raise ValidationError(_("¡Error! Existe solapamiento de horario"))
            elif len(after_midnight_recs) > 1:
                raise ValidationError(_("¡Error! Existe solapamiento de horario"))
            
            for it in range(len(att_ids)-1):
                if att_ids[it].hour_to > att_ids[it+1].hour_from:
                    raise ValidationError(_("¡Error! Existe solapamiento de horario"))
            break
            
    @api.onchange('hour_from')
    def _onchange_hour_from(self):
        # avoid negative
        self.hour_from = min(self.hour_from, 23.99)
        self.hour_from = max(self.hour_from, 0.0)

    @api.onchange('hour_to')
    def _onchange_hour_to(self):
        # avoid negative
        self.hour_to = min(self.hour_to, 23.99)
        self.hour_to = max(self.hour_to, 0.0)