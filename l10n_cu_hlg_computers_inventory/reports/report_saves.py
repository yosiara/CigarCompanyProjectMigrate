# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ReportSaves(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_saves'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_computers_inventory.report_saves')

        saves_list = self.env['computers_inventory.planning_saves'].search([])

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': saves_list,
            'elaborates_id': self.env['hr.employee'].search([('id', '=', data['elaborates_id'])]),
            'approved_id': self.env['hr.employee'].search([('id', '=', data['approved_id'])]),
        }

        return report_obj.render('l10n_cu_hlg_computers_inventory.report_saves', docargs)