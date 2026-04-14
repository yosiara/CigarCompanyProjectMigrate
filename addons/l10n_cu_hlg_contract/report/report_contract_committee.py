# -*- coding: utf-8 -*-
from odoo import api, models


class ReportContractCommittee(models.AbstractModel):
    _name = 'report.l10n_cu_contract.report_contract_committee'

    @api.model
    def render_html(self, docids, data=None):
        contract_obj = self.env['l10n_cu_contract.contract_agreement']

        #contract = contract_obj.search([('contract_id', '=', docids[0])])

        agreement = contract_obj.search([('number', '=', docids[0])])

        docargs = {
            #'docs': self.env['l10n_cu_contract.contract_committee'].browse(data['ids']),
            'docs': self.env['l10n_cu_contract.contract_committee'].search([('id', '=', docids)]),
            'agreement': agreement,
            #'contract': contract,
        }
        return self.env['report'].render('l10n_cu_contract.report_contract_committee', docargs)
