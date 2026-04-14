# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import pkg_resources


class ReportAuthorizedSoftwareDocx(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_auth_soft_docx'

    def get_report_values(self, docids, data=None):

        # if len(docids) > 1:
        #     raise UserError(_('This report is only available to select only one record...'))

        path = pkg_resources.resource_filename(
            "odoo.addons.l10n_cu_hlg_computers_inventory",
            "static/src/img/dummy_logo.png",
        )

        return {
            # 'objects': self.env['computers_inventory.authorized_software'].search([('id', 'in', docids)]),
            'replace_logo': {'src': 'path', 'data': path}
        }
