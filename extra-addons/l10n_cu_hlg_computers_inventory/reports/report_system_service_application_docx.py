# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import pkg_resources


class ReportSystemServiceApplicationDocx(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_sys_ser_app_docx'

    def get_report_values(self, docids, data=None):
        path = pkg_resources.resource_filename(
            "odoo.addons.l10n_cu_hlg_computers_inventory",
            "static/src/img/dummy_logo.png",
        )

        return {
            'replace_logo': {'src': 'path', 'data': path}
        }
