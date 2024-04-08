# -*- coding:utf-8 -*-

# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, models
from odoo.tools.translate import _


class ReportAuditPlan(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_audit_plan'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_computers_inventory.report_audit_plan')
        year = data['year']

        audit_plan_lis = self.env['computers_inventory.audit_plan'].search([('year', '=', year)])
        departments = {}

        for audit_plan in audit_plan_lis:
            if audit_plan.department_id.id not in departments:
                departments[audit_plan.department_id.id] = {'name': audit_plan.department_id.name,
                                                            'plan': {'01': False, '02': False, '03': False, '04': False,
                                                                     '05': False,
                                                                     '06': False, '07': False, '08': False, '09': False,
                                                                     '10': False,
                                                                     '11': False, '12': False}}
            departments[audit_plan.department_id.id]['plan'][audit_plan.month] = True

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': departments,
            'elaborates_id': self.env['hr.employee'].search([('id', '=', data['elaborates_id'])]),
            'approved_id': self.env['hr.employee'].search([('id', '=', data['approved_id'])]),
        }
        return report_obj.render('l10n_cu_hlg_computers_inventory.report_audit_plan', docargs)
