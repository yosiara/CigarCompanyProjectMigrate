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
from odoo import api, models,_, fields
from odoo.exceptions import UserError, ValidationError
from datetime import datetime,date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz

resp_dic = {'nokey': _(u'Usted debe solicitar una clave de registro válida. Por favor contacte al centro de soporte por una nueva.'),
            'invalidkey': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),
            'expkey': _(u'Usted está usando una clave vencida. Por favor contacte con el centro de soporte para una nueva.'),
            'invalidmod': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),}

month_dic = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
             '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}


class CalendarResumeGroupPlan(models.AbstractModel):
    _name = 'report.l10n_cu_calendar.report_group_resume_plan'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        data['enable_editor'] = 0
        model = self.env.context.get('active_model')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': model,
            'docs': data['docs'],
        }
        return report_obj.render('l10n_cu_calendar.report_group_resume_plan', docargs)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
