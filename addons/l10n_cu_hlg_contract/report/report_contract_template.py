# -*- coding: utf-8 -*-
from odoo import api, models


class ReportContractTemplate(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_contract.report_contract_template'

    @api.model
    def render_html(self, docids, data=None):
        docargs = {
            'data': data,
            'docs': self.env['l10n_cu_contract.contract'].browse(data['ids']),
        }
        return self.env['report'].render('l10n_cu_hlg_contract.report_contract_template', docargs)
