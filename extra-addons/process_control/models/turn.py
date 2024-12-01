# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools.float_utils import float_round

class Turn(models.Model):
    _name = "process_control.turn"
    _description = "Turn"

    name = fields.Char(required=True)
    turn_attendance_ids = fields.One2many('process_control.turn_attendance', inverse_name='turn_id', string='Working Time *', store=True, readonly=False, copy=True)

class TurnAttendance(models.Model):
    _name = "process_control.turn_attendance"
    _description = "Work Detail"

    name = fields.Char(string="Sesión *",required=True)
    hour_from = fields.Float(string='Work from *', required=True, index=True,
        help="Start and End time of working.\n"
             "A specific value of 24:00 is interpreted as 23:59:59.999999.")
    hour_to = fields.Float(string='Work to *', required=True)
    turn_id = fields.Many2one("process_control.turn", string="Turn *", required=True, ondelete='cascade')

    #_inherit = 'resource.calendar'

    # name = fields.Char(required=False, copy=False)
    # description = fields.Text(string="Descripción", required=False, )
    # attendance_ids = fields.One2many(
    #     'resource.calendar.attendance', 'calendar_id', string='Sesión',
    #     copy=True, required=True)

    # _sql_constraints = [('name_uniq', 'unique (name)', "El turno de trabajo ya existe.")]
