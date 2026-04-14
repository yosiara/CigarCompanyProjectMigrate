# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from odoo.addons.calendar.models.calendar import get_real_ids


class Partner(models.Model):
    _inherit = 'res.partner'

    # COLUMNS--------------------------
    boss_id = fields.Many2one('res.partner', string='Boss')
    subordinate_ids = fields.One2many('res.partner', 'boss_id', string='Subordinates')
    department_id = fields.Many2one('hr.department', string='Department')
    partner_group_ids = fields.Many2many('l10n_cu_calendar.org_group', 'l10n_cu_calendar_org_group_partner_group',
                                         'partner_id', 'group_id', string='Organizational groups to which it belongs')
    # END COLUMNS--------------------------

    # To avoid errors in this function when calendar.event is in a x2many field and they have virtual ids like 'one2many_v_id_'
    @api.multi
    def get_attendee_detail(self, meeting_id):
        """ Return a list of tuple (id, name, status)
            Used by web_calendar.js : Many2ManyAttendee
        """
        datas = []
        meeting = None
        if meeting_id and (isinstance(meeting_id, int) or (isinstance(meeting_id, basestring) and not meeting_id.startswith('one2many_v_id_'))):
            meeting = self.env['calendar.event'].browse(get_real_ids(meeting_id))

        for partner in self:
            data = partner.name_get()[0]
            data = [data[0], data[1], False, partner.color]
            if meeting:
                for attendee in meeting.attendee_ids:
                    if attendee.partner_id.id == partner.id:
                        data[2] = attendee.state
            datas.append(data)
        return datas