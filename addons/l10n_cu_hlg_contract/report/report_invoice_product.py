# -*- coding: utf-8 -*-
from odoo import api, models, fields, tools


class ReportInvoiceProduct(models.Model):
    _name = "report.invoice.product"
    _auto = False

    invoice_code = fields.Char('Código de facturación', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Cliente', readonly=True)
    reeup = fields.Char('REEUP', readonly=True)
    municipality_id = fields.Many2one('l10n_cu_base.municipality', 'Municipality')
    contract_id = fields.Many2one('l10n_cu_contract.contract', 'Contract')
    invoice_id = fields.Many2one('account.invoice', 'Factura')
    date = fields.Date('Fecha')
    product_id = fields.Many2one('product.product', 'Producto', readonly=True)
    amount_cup = fields.Float('Importe CUP')
    amount_cuc = fields.Float('Importe CUC')
    national_contract = fields.Boolean('Contrato Nacional', default=False, help="")

    def init(self):
        tools.drop_view_if_exists(self._cr, 'report_invoice_product')
        self._cr.execute("""
            CREATE or REPLACE view report_invoice_product as (
                select
                    inv.id AS id, 
                    prod.default_code AS invoice_code, 
                    part.id AS partner_id, 
                    part.reeup_code AS reeup,
                    mun.id AS municipality_id,
                    cont.id AS contract_id, 
                    inv.id AS invoice_id, 
                    inv.date_invoice AS date,
                    prod.id AS product_id, 
                    line.price_subtotal as amount_cup,
                    cont.national_contract as national_contract
                from account_invoice AS inv
                    left join res_partner AS part ON inv.partner_id = part.id
                    left join l10n_cu_base_municipality AS mun ON inv.municipality_id = mun.id
                    left join l10n_cu_contract_contract AS cont ON inv.contract_id = cont.id
                    left join account_invoice_line AS line ON inv.id = line.invoice_id
                    left join product_product AS prod ON prod.id = line.product_id
                where inv.state != ANY(array['cancel'])
            )
        """)