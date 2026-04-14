# -*- coding: utf-8 -*-
from odoo import api, models
from datetime import datetime, timedelta

report_name = 'l10n_cu_hlg_hr.report_registration_attendance'

class RegistrationAttendanceReport(models.AbstractModel):
    _name = 'report.' + report_name

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name(report_name)
        obj = self.env['hr.employee']

        if docids is None:
            doc_ids = data['ids']

        if len(doc_ids) == 0 :
            doc_ids = obj.search([], order="parent_id asc, code asc")
        else:
            doc_ids = obj.search([('id','in', doc_ids)], order="parent_id asc, code asc")

        employees = obj.browse(doc_ids.ids)

        MESES = {'1': 'Enero', '2': 'Febrero', '3': 'Marzo', '4': 'Abril', '5': 'Mayo', '6': 'Junio',
                 '7': 'Julio', '8': 'Agosto', '9': 'Septiembre', '10': 'Octubre', '11': 'Noviembre', '12': 'Diciembre'}
        year = data['form']['year']
        mes = data['form']['mes']
        nombre_mes = MESES[mes]
        shows_sat_sun = data['form']['shows_sat_sun']

        docargs = {
            'doc_ids': doc_ids,
            'doc_model': report.model,
            'docs': employees,
            'mes': mes,
            'nombre_mes': nombre_mes,
            'shows_sat_sun': shows_sat_sun,
            'anho': year
        }
        return report_obj.render(report_name, docargs)
