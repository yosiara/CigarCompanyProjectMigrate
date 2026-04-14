# -*- coding: utf-8 -*-
##############################################################################
#

from odoo import api, models, SUPERUSER_ID, fields
from calendar import Calendar
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import pytz
from odoo.tools.translate import _

resp_dic = {'nokey': _(u'Usted debe solicitar una clave de registro válida. Por favor contacte al centro de soporte por una nueva.'),
            'invalidkey': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),
            'expkey': _(u'Usted está usando una clave vencida. Por favor contacte con el centro de soporte para una nueva.'),
            'invalidmod': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),}


class CalendarReportIndividualPlan(models.AbstractModel):
    _name = 'report.l10n_cu_calendar.report_individual_plan'

    @api.multi
    def render_html(self, docids, data=None):
        model = self.env.context.get('active_model')
        docargs = {
            'doc_ids': self._ids,
            'doc_model': model,
            'docs': data['docs']
        }
        report_obj = self.env['report']
        # Busqueda del user
        user = self.env['res.users'].search([('id', '=', self._uid)])
        if user.company_id.individual_plan_one_page:
            return report_obj.render('l10n_cu_calendar.report_individual_plan_one_page', docargs)
        else:
            return report_obj.render('l10n_cu_calendar.report_individual_plan', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: