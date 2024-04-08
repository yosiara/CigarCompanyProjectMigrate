# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import pkg_resources


class ReportSavesDocx(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_saves_docx'

    @api.model
    def get_report_values(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_computers_inventory.report_saves_docx')

        saves_list = self.env['computers_inventory.planning_saves'].search([])

        path = pkg_resources.resource_filename(
            "odoo.addons.l10n_cu_hlg_computers_inventory",
            "static/src/img/dummy_logo.png",
        )

        return {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': saves_list,
            'elaborates_id': self.env['hr.employee'].search([('id', '=', data['elaborates_id'])]),
            'approved_id': self.env['hr.employee'].search([('id', '=', data['approved_id'])]),
            'replace_logo': {'src': 'path', 'data': path}
        }
