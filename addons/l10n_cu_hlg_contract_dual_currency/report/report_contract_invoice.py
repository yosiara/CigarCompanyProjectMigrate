# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class ContractReport(models.Model):
    _inherit = "contract.report"

    amount_cup = fields.Float('Amount CUP', readonly=True, group_operator="avg")
    amount_cuc = fields.Float('Amount CUC', readonly=True, group_operator="avg")
    amount_invoice_cup = fields.Float('Amount Invoice CUP', readonly=True)
    amount_invoice_cuc = fields.Float('Amount Invoice CUC', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'contract_report')
        self._cr.execute("""
            CREATE or REPLACE view contract_report as (
                SELECT
                    contract.id as id,
                    contract.number as contract_number,
                    contract.partner_id as partner_id,
                    contract.total_cup as amount_cup,
                    contract.total_cuc as amount_cuc,
                    contract.amount_total as amount_total,
                    invoice.amount_total_cup as amount_invoice_cup,
                    invoice.amount_total_cuc as amount_invoice_cuc,
                    invoice.amount_total_cup + invoice.amount_total_cuc as amount_invoice,
                    invoice.reference as invoice_ref,
                    invoice.date as invoice_date,
                    contract.flow AS flow

                FROM
                    l10n_cu_contract_contract as contract
                    INNER JOIN account_invoice as invoice ON contract.id=invoice.contract_id
            )
        """)