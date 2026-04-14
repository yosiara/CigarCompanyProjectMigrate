# -*- coding: utf-8 -*-
##############################################################################
from odoo.http import request
import datetime
from datetime import date
from odoo import api, fields, models, _
import json
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class ContractPurchaseDashboard(models.Model):
    _name = 'contract.purchase.dashboard'
    _description = 'Purchase Contract Dashboard'

    name = fields.Char("Name")

    @api.model
    def get_data_info(self):
        uid = request.session.uid
        cr = self.env.cr
        year = str(date.today())[0:4]
        data_info = []
        invoices_labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre',
                           'Octubre', 'Noviembre', 'Diciembre']
        state = ('open', 'paid')
        query_sum = """
                    select sum(amount_total) as amount_total, count(id) as count
                    from account_invoice
                    where cast(date_invoice as varchar) like %s and state in %s and type = 'in_invoice';
                """
        cr.execute(query_sum, (year + '-01%', state))
        sum_total_ene = cr.dictfetchall()
        if len(sum_total_ene) > 0:
            total_ene = sum_total_ene[0]['amount_total']
            count_ene = sum_total_ene[0]['count']
        else:
            total_ene = 0
            count_ene = 0

        cr.execute(query_sum, (year + '-02%', state))
        sum_total_feb = cr.dictfetchall()
        if len(sum_total_feb) > 0:
            total_feb = sum_total_feb[0]['amount_total']
            count_feb = sum_total_feb[0]['count']
        else:
            total_feb = 0
            count_feb = 0

        cr.execute(query_sum, (year + '-03%', state))
        sum_total_mar = cr.dictfetchall()
        if len(sum_total_mar) > 0:
            total_mar = sum_total_mar[0]['amount_total']
            count_mar = sum_total_mar[0]['count']
        else:
            total_mar = 0
            count_mar = 0

        cr.execute(query_sum, (year + '-04%', state))
        sum_total_abr = cr.dictfetchall()
        if len(sum_total_abr) > 0:
            total_abr = sum_total_abr[0]['amount_total']
            count_abr = sum_total_abr[0]['count']
        else:
            total_abr = 0
            count_abr = 0

        cr.execute(query_sum, (year + '-05%', state))
        sum_total_may = cr.dictfetchall()
        if len(sum_total_may) > 0:
            total_may = sum_total_may[0]['amount_total']
            count_may = sum_total_may[0]['count']
        else:
            total_may = 0
            count_may = 0

        cr.execute(query_sum, (year + '-06%', state))
        sum_total_jun = cr.dictfetchall()
        if len(sum_total_jun) > 0:
            total_jun = sum_total_jun[0]['amount_total']
            count_jun = sum_total_jun[0]['count']
        else:
            total_jun = 0
            count_jun = 0

        cr.execute(query_sum, (year + '-07%', state))
        sum_total_jul = cr.dictfetchall()
        if len(sum_total_jul) > 0:
            total_jul = sum_total_jul[0]['amount_total']
            count_jul = sum_total_jul[0]['count']
        else:
            total_jul = 0
            count_jul = 0

        cr.execute(query_sum, (year + '-08%', state))
        sum_total_ago = cr.dictfetchall()
        if len(sum_total_ago) > 0:
            total_ago = sum_total_ago[0]['amount_total']
            count_ago = sum_total_ago[0]['count']
        else:
            total_ago = 0
            count_ago = 0

        cr.execute(query_sum, (year + '-09%', state))
        sum_total_sep = cr.dictfetchall()
        if len(sum_total_sep) > 0:
            total_sep = sum_total_sep[0]['amount_total']
            count_sep = sum_total_sep[0]['count']
        else:
            total_sep = 0
            count_sep = 0

        cr.execute(query_sum, (year + '-10%', state))
        sum_total_oct = cr.dictfetchall()
        if len(sum_total_oct) > 0:
            total_oct = sum_total_oct[0]['amount_total']
            count_oct = sum_total_oct[0]['count']
        else:
            total_oct = 0
            count_oct = 0

        cr.execute(query_sum, (year + '-11%', state))
        sum_total_nov = cr.dictfetchall()
        if len(sum_total_nov) > 0:
            total_nov = sum_total_nov[0]['amount_total']
            count_nov = sum_total_nov[0]['count']
        else:
            total_nov = 0
            count_nov = 0

        cr.execute(query_sum, (year + '-12%', state))
        sum_total_dic = cr.dictfetchall()
        if len(sum_total_dic) > 0:
            total_dic = sum_total_dic[0]['amount_total']
            count_dic = sum_total_dic[0]['count']
        else:
            total_dic = 0
            count_dic = 0

        invoices_total_by_month = list()
        invoices_total_by_month.append(total_ene)
        invoices_total_by_month.append(total_feb)
        invoices_total_by_month.append(total_mar)
        invoices_total_by_month.append(total_abr)
        invoices_total_by_month.append(total_may)
        invoices_total_by_month.append(total_jun)
        invoices_total_by_month.append(total_jul)
        invoices_total_by_month.append(total_ago)
        invoices_total_by_month.append(total_sep)
        invoices_total_by_month.append(total_oct)
        invoices_total_by_month.append(total_nov)
        invoices_total_by_month.append(total_dic)
        invoices_by_month = list()
        invoices_by_month.append(count_ene)
        invoices_by_month.append(count_feb)
        invoices_by_month.append(count_mar)
        invoices_by_month.append(count_abr)
        invoices_by_month.append(count_may)
        invoices_by_month.append(count_jun)
        invoices_by_month.append(count_jul)
        invoices_by_month.append(count_ago)
        invoices_by_month.append(count_sep)
        invoices_by_month.append(count_oct)
        invoices_by_month.append(count_nov)
        invoices_by_month.append(count_dic)

        contract_sql_due_date = """
                        select c.number, c.name as contract, p.name as partner, ct.name as type, c.date_end as date
                            from l10n_cu_contract_contract c, l10n_cu_contract_contract_type ct, res_partner p
                            where c.partner_id = p.id and c.contract_type = ct.id
                            and c.flow = 'supplier' and c.date_end >= %s and c.state = 'open'
                            order by c.date_end asc limit 10;
                        """
        date_current = str(date.today())
        cr.execute(contract_sql_due_date, (date_current,))
        contract_due = cr.dictfetchall()
        contract_sql_due_percent = """
                                select c.number, c.name as contract, p.name as partner, c.amount_total as amount_total,
							            c.amount_invoice as amount_invoice,
							            c.amount_rest as amount_rest,
							            c.percentage_execution as percentage_execution
                                        from l10n_cu_contract_contract c, res_partner p
                                        where c.partner_id = p.id
                                        and c.flow = 'supplier' and c.state = 'open'
                                        and c.percentage_execution>=%s
                                        order by c.percentage_execution DESC limit 10;
                                """
        percentage = self.env['ir.config_parameter'].sudo().get_param('contract_monetary')
        if not percentage:
            percentage = 75
        cr.execute(contract_sql_due_percent, (percentage,))
        contract_due_1 = cr.dictfetchall()
        contract_table = list()
        contract_table_1 = list()
        for c in contract_due:
            dicc_c = dict()
            dicc_c['number'] = c['number']
            dicc_c['name'] = c['contract']
            dicc_c['partner'] = c['partner']
            dicc_c['type'] = c['type']
            dicc_c['date'] = c['date'][8:10] + '/' + c['date'][5:7] + '/' + c['date'][0:4] if c['date'] else '-'
            contract_table.append(dicc_c)
        for c in contract_due_1:
            dicc_c = dict()
            dicc_c['number'] = c['number']
            dicc_c['name'] = c['contract']
            dicc_c['partner'] = c['partner']
            dicc_c['total'] = "{0:.2f}".format(c['amount_total']).replace('.', ',') if c['amount_total'] else '0,00'
            dicc_c['execute'] = "{0:.2f}".format(c['amount_invoice']).replace('.', ',') if c['amount_invoice'] else '0,00'
            dicc_c['residual'] = "{0:.2f}".format(c['amount_rest']).replace('.', ',') if c['amount_rest'] else '0,00'
            dicc_c['percent'] = "{0:.2f}".format(c['percentage_execution']).replace('.', ',') if c['percentage_execution'] else '0,00'
            contract_table_1.append(dicc_c)

        view_invoice_p_id = self.env.ref('l10n_cu_hlg_contract_sale_dashboard.invoice_tree_dashboard_purchase').id
        data = {
            'contract_count': self.env['l10n_cu_contract.contract'].sudo().search_count([('flow', '=', 'supplier'), ('state','=', 'open'),('parent_id', '=', False)]),
            'contract_count_draft': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'draft'),('parent_id', '=', False)]),
            'contract_count_pending_dict': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'pending_dict'),('parent_id', '=', False)]),
            'contract_count_pending_appro': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'pending_appro'),('parent_id', '=', False)]),
            'contract_count_approval': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'approval'),('parent_id', '=', False)]),
            'contract_count_pending_signed': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'pending_signed'),('parent_id', '=', False)]),
            'contract_count_open': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'open'),('parent_id', '=', False)]),
            'contract_count_close': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'close'),('parent_id', '=', False)]),
            'contract_count_cancelled': self.env['l10n_cu_contract.contract'].sudo().search_count(
                [('flow', '=', 'supplier'), ('state', '=', 'cancelled'),('parent_id', '=', False)]),
            'invoice_count': self.env['account.invoice'].sudo().search_count([('date_invoice', 'like', year),
                                                                              ('type', '=', 'in_invoice')]),
            'invoice_count_draft': self.env['account.invoice'].sudo().search_count([('date_invoice', 'like', year),
                                                                                    ('type', '=', 'in_invoice'),
                                                                                    ('state', '=', 'draft')]),
            'invoice_count_open': self.env['account.invoice'].sudo().search_count([('date_invoice', 'like', year),
                                                                                   ('type', '=', 'in_invoice'),
                                                                                   ('state', '=', 'open')]),
            'invoice_count_paid': self.env['account.invoice'].sudo().search_count([('date_invoice', 'like', year),
                                                                                   ('type', '=', 'in_invoice'),
                                                                                   ('state', '=', 'paid')]),
            'invoice_count_cancelled': self.env['account.invoice'].sudo().search_count([('date_invoice', 'like', year),
                                                                                        ('type', '=', 'in_invoice'),
                                                                                        ('state', '=', 'cancelled')]),
            'invoices_labels': invoices_labels,
            'invoices_total_by_month': invoices_total_by_month,
            'invoices_by_month': invoices_by_month,
            'contract_table': contract_table,
            'contract_table_1': contract_table_1,
            'view_invoice_p_id': view_invoice_p_id,
        }
        data_info.append(data)
        return data_info
