# -*- coding: utf-8 -*-
from odoo import api, models


class ReportContractToExpirePercent(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_contract.report_contract_to_expire_percent'

    @api.model
    def render_html(self, docids, data=None):
        percent = data['percent']
        flow = data['flow']
        contracts = self.env['l10n_cu_contract.contract'].search([('flow', '=', flow),
                                                                  ('state', 'in', ['open']),
                                                                  ('percentage_execution', '>=', percent)],
                                                                 order='percentage_execution asc')
        docargs = {
            'data': data,
            'docs': contracts,
            'percent': '{0:.2f}'.format(percent).replace('.', ','),
            'flow': flow
        }
        return self.env['report'].render('l10n_cu_hlg_contract.report_contract_to_expire_percent', docargs)
