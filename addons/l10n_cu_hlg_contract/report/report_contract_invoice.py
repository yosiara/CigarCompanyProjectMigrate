# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class ContractReport(models.Model):
    _name = "contract.report"
    _auto = False

    contract_number = fields.Char('Contract Number', readonly=True)
    amount_total = fields.Float('Amount Total', readonly=True, group_operator="avg")
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    amount_invoice = fields.Float('Amount Invoice', readonly=True)
    invoice_id = fields.Many2one('account.invoice', 'Invoice', readonly=True)
    #invoice_ref = fields.Char('Invoice Reference', readonly=True)
    invoice_date = fields.Date('Date Invoice', readonly=True)
    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)

    def init(self):
        tools.drop_view_if_exists(self._cr, 'contract_report')
        self._cr.execute("""
            CREATE or REPLACE view contract_report as (
                SELECT 
                    contract.id as id,
                    contract.number as contract_number,
                    contract.partner_id as partner_id,
                    contract.amount_total as amount_total,
                    invoice.amount_total as amount_invoice,
                    invoice.date as invoice_date,
                    contract.flow AS flow
                    
                FROM
                    l10n_cu_contract_contract as contract
                    INNER JOIN account_invoice as invoice ON contract.id=invoice.contract_id
            )
        """)