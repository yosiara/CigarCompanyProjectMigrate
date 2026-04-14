# -*- coding: utf-8 -*-

from odoo import api, models, SUPERUSER_ID, fields
import pytz
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

resp_dic = {'nokey': _(u'Usted debe solicitar una clave de registro válida. Por favor contacte al centro de soporte por una nueva.'),
            'invalidkey': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),
            'expkey': _(u'Usted está usando una clave vencida. Por favor contacte con el centro de soporte para una nueva.'),
            'invalidmod': _(u'Usted está usando una clave inválida. Por favor contacte con el centro de soporte para una nueva.'),}

month_dic = {'01': 'enero', '02': 'febrero', '03': 'marzo', '04': 'abril', '05': 'mayo', '06': 'junio',
             '07': 'julio', '08': 'agosto', '09': 'septiembre', '10': 'octubre', '11': 'noviembre', '12': 'diciembre'}


class CalendarReportIndividualPlanResumen(models.AbstractModel):
    _name = 'report.l10n_cu_calendar.report_individual_plan_resumen'

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
        return report_obj.render('l10n_cu_calendar.report_individual_plan_resumen', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
