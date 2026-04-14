# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from lxml import etree
from datetime import timedelta
import pytz
import datetime


def seconds(td):
    assert isinstance(td, timedelta)

    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10.**6


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    rotating_calendar = fields.Boolean('Rotating calendar')
    turn_process_control = fields.Boolean('Turn process control')
    calendar_date_from = fields.Date('Calendar date from',
                                     help='Working calendar start date. Used to calculate the shift exact date.')
    sgp_turn_id = fields.Many2one('hr_sgp_integration.turn')

    initial_rotation = fields.Selection([
        ('0', '1ra'),
        ('1', '2da'),
        ('2', '3ra'),
        ('3', '4ta'),
        ('4', '5ta'),
        ('5', '6ta'),
        ('6', '7ma'),
        ('7', '8va'),
        ('8', '9na'),
        ('9', '10ma'),
        ('10', '11na'),
        ('11', '12va'),
        ('12', '13ra'),
        ('13', '14ta')
    ], 'Initial Rotation')
    leave_count = fields.Integer(
        compute='_compute_leave_count', string='Leaves')

    @api.onchange('calendar_date_from', 'rotating_calendar')
    def _compute_initial_rotation(self):
        if self.calendar_date_from and self.rotating_calendar:
            calendar_date_from = fields.Date.from_string(self.calendar_date_from)
            weekday = calendar_date_from.weekday()
            rotation = 1e9
            for att in self.attendance_ids:
                if int(att.dayofweek) == weekday:
                    rotation = min(rotation, int(att.rotation))

            if rotation is not 1e9:
                self.initial_rotation = str(rotation)

    @api.multi
    def _compute_leave_count(self):
        for calendar in self:
            calendar.leave_count = len(calendar.leave_ids)

    @api.multi
    def get_weekdays(self, default_weekdays=None):
        """ Return the list of weekdays that contain at least one working interval.
        If no id is given (no calendar), return default weekdays. """
        if self and self.rotating_calendar:
            return default_weekdays if default_weekdays is not None else [0, 1, 2, 3, 4, 5, 6]
        else:
            return super(ResourceCalendar, self).get_weekdays(default_weekdays=default_weekdays)

    @api.multi
    def get_attendances_for_weekday(self, date):
        """ Given a list of weekdays, return matching resource.calendar.attendance"""
        if self and self.rotating_calendar:
            self.ensure_one()
            # buscar la fecha de inicio del calendar
            calendar_date_from = fields.Date.from_string(self.calendar_date_from)
            # hallar el turno que le toca a la fecha
            rotations = []
            for rot in self.attendance_ids:
                if rot.rotation not in rotations:
                    rotations.append(rot.rotation)
            days_difference = (date.date() - calendar_date_from).days
            if (days_difference - (len(rotations) - int(self.initial_rotation))) >= 0:
                rotation = (days_difference - (len(rotations) - int(self.initial_rotation))) % len(rotations)
            else:
                rotation = int(self.initial_rotation) + days_difference
            attendances = self.env['resource.calendar.attendance']
            date_string = fields.Date.to_string(date)
            for attendance in self.attendance_ids.filtered(lambda att: int(att.rotation) == rotation and
                                                                       not ((
                                                                                    att.date_from and date_string < att.date_from) or (
                                                                                    att.date_to and date_string > att.date_to))):
                attendances |= attendance
            return attendances
        else:
            return super(ResourceCalendar, self).get_attendances_for_weekday(date)

    @api.model
    def interval_remove_leaves(self, interval, leave_intervals):
        """ Utility method that remove leave intervals from a base interval:

         - clean the leave intervals, to have an ordered list of not-overlapping
           intervals
         - initiate the current interval to be the base interval
         - for each leave interval:

          - finishing before the current interval: skip, go to next
          - beginning after the current interval: skip and get out of the loop
            because we are outside range (leaves are ordered)
          - beginning within the current interval: close the current interval
            and begin a new current interval that begins at the end of the leave
            interval
          - ending within the current interval: update the current interval begin
            to match the leave interval ending

        :param tuple interval: a tuple (beginning datetime, ending datetime) that
                               is the base interval from which the leave intervals
                               will be removed
        :param list leave_intervals: a list of tuples (beginning datetime, ending datetime)
                                    that are intervals to remove from the base interval
        :return list intervals: a list of tuples (begin datetime, end datetime, attendance_id int)
                                that are the remaining valid intervals """
        if not interval:
            return interval
        if leave_intervals is None:
            leave_intervals = []
        intervals = []
        leave_intervals = self.interval_clean(leave_intervals)
        current_interval = [interval[0], interval[1], interval[2] if len(interval) > 2 else None]
        for leave in leave_intervals:
            if leave[1] <= current_interval[0]:
                continue
            if leave[0] >= current_interval[1]:
                break
            if current_interval[0] < leave[0] < current_interval[1]:
                current_interval[1] = leave[0]
                intervals.append((current_interval[0], current_interval[1], current_interval[2]))
                current_interval = [leave[1], interval[1]]
            if current_interval[0] <= leave[1]:
                current_interval[0] = leave[1]
        if current_interval and current_interval[0] < interval[1]:  # remove intervals moved outside base interval due to leaves
            intervals.append((current_interval[0], current_interval[1], current_interval[2]))
        return intervals

    @api.multi
    def get_working_hours_of_date(self, start_dt=None, end_dt=None,
                                  leaves=None, compute_leaves=False, resource_id=None,
                                  default_interval=None):
        """ Get the working hours of the day based on calendar. This method uses
        get_working_intervals_of_day to have the work intervals of the day. It
        then calculates the number of hours contained in those intervals. """
        res = timedelta()
        intervals = self.get_working_intervals_of_day(
            start_dt, end_dt, leaves,
            compute_leaves, resource_id,
            default_interval)
        for interval in intervals:
            if len(interval) > 2 and interval[2] is not None:
                attendance = self.env['resource.calendar.attendance'].search([('id', '=', interval[2])])
                res += interval[1] - interval[0] - timedelta(seconds=(attendance.rest_time * 3600))
            else:
                res += interval[1] - interval[0]

        return seconds(res) / 3600.0

    @api.onchange('rotating_calendar')
    def onchange_rotation_calendar(self):
        context = dict(self._context)
        context.update({'rotating_calendar': self.rotating_calendar})
        self.with_context(context).env['resource.calendar.attendance'].fields_view_get(None, 'tree')


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"
    _order = 'rotation_integer,dayofweek,hour_from'

    rotation_integer = fields.Integer('Rotation Integer', compute='compute_rotation_integer', store=True)

    rotation = fields.Selection([
        ('0', '1ra'),
        ('1', '2da'),
        ('2', '3ra'),
        ('3', '4ta'),
        ('4', '5ta'),
        ('5', '6ta'),
        ('6', '7ma'),
        ('7', '8va'),
        ('8', '9na'),
        ('9', '10ma'),
        ('10', '11na'),
        ('11', '12va'),
        ('12', '13ra'),
        ('13', '14ta')
    ], 'Rotation', required=True, index=True, default='0')

    @api.depends('rotation')
    def compute_rotation_integer(self):
        for record in self:
            if record.rotation:
                record.rotation_integer = int(record.rotation)

    @api.model
    def fields_view_get(self, view_id=None, view_type=False, toolbar=False, submenu=False):
        context = self._context

        rotation = context.get('rotating_calendar')

        res = super(ResourceCalendarAttendance, self).fields_view_get(view_id=view_id, view_type=view_type,
                                                                      toolbar=toolbar,
                                                                      submenu=submenu)

        if view_type == 'tree':
            doc = etree.XML(res['arch'])

            if rotation:
                for node in doc.xpath("//field[@name='rotation']"):
                    node.set('invisible', '0')
                    node.set('modifiers', '{"tree_invisible": false}')

            res['arch'] = etree.tostring(doc)
        return res
