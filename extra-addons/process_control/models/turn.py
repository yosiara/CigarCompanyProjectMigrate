# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Turn(models.Model):
    _name = "process_control.turn"
    _description = "Turn"

    name = fields.Char(required=True)
    turn_attendance_ids = fields.One2many('process_control.turn_attendance', inverse_name='turn_id', string='Working Time *', store=True, readonly=False, copy=True)