# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Turn(models.Model):
    _inherit = 'resource.calendar'



    name = fields.Char(required=False, copy=False)
    description = fields.Text(string="Descripción", required=False, )
    attendance_ids = fields.One2many(
        'resource.calendar.attendance', 'calendar_id', string='Sesión',
        copy=True, required=True)

    _sql_constraints = [('name_uniq', 'unique (name)', "El turno de trabajo ya existe.")]
