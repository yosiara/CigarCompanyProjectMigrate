# -*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models
from odoo.tools.translate import _


class ReportInspection(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_inspection'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_computers_inventory.report_inspection')
        start_date = data['start_date']
        end_date = data['end_date']
        result = []

        inspections_list = self.env['computers_inventory.inspection'].search([('date', '>=', start_date), ('date', '<=', end_date)],
                                                         order='date')

        for inspection in inspections_list:
            res = {}
            res['equipment_id'] = inspection.equipment_id
            res['date'] = inspection.date
            res['department_id'] = inspection.department_id
            res['observations'] = inspection.observations
            res['participants_ids'] = inspection.participants_ids
            res['security_incident_ids'] = inspection.security_incident_ids
            res['conclusions'] = inspection.conclusions
            result.append(res)

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': result,
            'elaborates_id': self.env['hr.employee'].search([('id', '=', data['elaborates_id'])]),
            'approved_id': self.env['hr.employee'].search([('id', '=', data['approved_id'])]),
        }
        return report_obj.render('l10n_cu_hlg_computers_inventory.report_inspection', docargs)
