# -*- coding: utf-8 -*-

from odoo import models, fields


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"
    init_date = fields.Date()


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"
    rest_time = fields.Float(string='Rest time', required=False, default=0.0)
