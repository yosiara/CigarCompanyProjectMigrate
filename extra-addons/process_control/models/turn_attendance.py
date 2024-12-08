# -*- coding: utf-8 -*-
from odoo import api, fields, models

class TurnAttendance(models.Model):
    _name = "process_control.turn_attendance"
    _description = "Work Detail"

    name = fields.Char(string="Sesión *",required=True)
    hour_from = fields.Float(string='Work from *', required=True,
        help="Start of working.\nA specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to *', required=True,
        help="End of working.\nA specific value of 24:00 is interpreted as 23:59:59.999999.")
    turn_id = fields.Many2one("process_control.turn", string="Turn *", required=True, ondelete='cascade')
