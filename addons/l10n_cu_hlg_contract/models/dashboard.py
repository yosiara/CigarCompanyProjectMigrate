# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang


class DashboardCommercial(models.Model):
    _name = 'dashboard.commercial'

    name = fields.Char('Name')
    color = fields.Integer('Color')
    kanban_dashboard_graph_contract = fields.Text(compute='_kanban_dashboard_graph_contract')
    kanban_dashboard = fields.Text(compute='_kanban_dashboard')
    total = fields.Integer(compute='_compute_total')

    @api.one
    def _kanban_dashboard(self):
        self.kanban_dashboard = json.dumps(self.get_journal_dashboard_datas())

    @api.one
    def _compute_total(self):
        flow = self.name
        company = self.env.user.company_id
        self.total = len(
            self.env['l10n_cu_contract.contract'].search([('flow', '=', flow), ('company_id', 'child_of', company.id)]))

    @api.multi
    def get_journal_dashboard_datas(self):
        company = self.env.user.company_id
        currency = company.currency_id
        contract_obj = self.env['l10n_cu_contract.contract']
        contracts_draft = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'draft'), ('company_id', 'child_of', company.id)])
        contracts_pend_dict = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'pending_dict'), ('company_id', 'child_of', company.id)])
        contracts_pend_ap = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'pending_appro'), ('company_id', 'child_of', company.id)])
        contracts_reje = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'rejected'), ('company_id', 'child_of', company.id)])
        contracts_app = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'approval'), ('company_id', 'child_of', company.id)])
        contracts_pend_sing = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'pending_signed'), ('company_id', 'child_of', company.id)])
        contracts_open = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'open'), ('company_id', 'child_of', company.id)])
        contracts_close = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'close'), ('company_id', 'child_of', company.id)])
        contracts_can = contract_obj.search(
            [('flow', '=', self.name), ('state', '=', 'cancelled'), ('company_id', 'child_of', company.id)])

        return {
            'number_draft': len(contracts_draft),
            'number_pend_dict': len(contracts_pend_dict),
            'number_pend_ap': len(contracts_pend_ap),
            'number_reje': len(contracts_reje),
            'number_app': len(contracts_app),
            'number_pend_sing': len(contracts_pend_sing),
            'number_open': len(contracts_open),
            'number_close': len(contracts_close),
            'number_can': len(contracts_can),

            'sum_draft': formatLang(self.env, currency.round(sum(contracts_draft.mapped('amount_total'))),
                                    currency_obj=currency),
            'sum_pend_dict': formatLang(self.env, currency.round(sum(contracts_pend_dict.mapped('amount_total'))),
                                        currency_obj=currency),
            'sum_pend_ap': formatLang(self.env, currency.round(sum(contracts_pend_ap.mapped('amount_total'))),
                                      currency_obj=currency),
            'sum_reje': formatLang(self.env, currency.round(sum(contracts_reje.mapped('amount_total'))),
                                   currency_obj=currency),
            'sum_app': formatLang(self.env, currency.round(sum(contracts_app.mapped('amount_total'))),
                                  currency_obj=currency),
            'sum_pend_sing': formatLang(self.env, currency.round(sum(contracts_pend_sing.mapped('amount_total'))),
                                        currency_obj=currency),
            'sum_open': formatLang(self.env, currency.round(sum(contracts_open.mapped('amount_total'))),
                                   currency_obj=currency),
            'sum_close': formatLang(self.env, currency.round(sum(contracts_close.mapped('amount_total'))),
                                    currency_obj=currency),
            'sum_can': formatLang(self.env, currency.round(sum(contracts_can.mapped('amount_total'))),
                                  currency_obj=currency),

            'currency_id': currency.id,
        }

    @api.multi
    def get_bar_graph_datas(self):
        data = []
        company = self.env.user.company_id
        flow = self.name
        today = datetime.strptime(fields.Date.context_today(self), DF)
        day_of_week = int(format_datetime(today, 'e', locale=self._context.get('lang') or 'en_US'))
        first_day_of_week = today + timedelta(days=-day_of_week + 1)

        contract_obj = self.env['l10n_cu_contract.contract']

        for i in range(-1, 3):
            value = 0
            if i == 0:
                label = _('This Week')
                last_day_of_week = first_day_of_week + timedelta(days=6)
                ids_contract = contract_obj.search(
                    [('flow', '=', flow), ('date_end', '>=', first_day_of_week),
                     ('date_end', '<=', last_day_of_week), ('company_id', '=', company.id)])
                value = int(len(ids_contract))
                data.append(
                    {'flow': flow, 'label': label, 'value': value, 'start_date': first_day_of_week.strftime(DF),
                     'last_date': last_day_of_week.strftime(DF)})
            else:
                start_week = first_day_of_week + timedelta(days=i * 7)
                end_week = start_week + timedelta(days=6)
                ids_contract = contract_obj.search(
                    [('flow', '=', flow), ('date_end', '>=', start_week),
                     ('date_end', '<=', end_week), ('company_id', '=', company.id)])
                value = int(len(ids_contract))
                if start_week.month == end_week.month:
                    label = str(start_week.day) + '-' + str(end_week.day) + ' ' + format_date(end_week, 'MMM',
                                                                                              locale=self._context.get(
                                                                                                  'lang') or 'en_US')
                else:
                    label = format_date(start_week, 'd MMM',
                                        locale=self._context.get('lang') or 'en_US') + '-' + format_date(end_week,
                                                                                                         'd MMM',
                                                                                                         locale=self._context.get(
                                                                                                             'lang') or 'en_US')
                data.append(
                    {'flow': flow, 'label': label, 'value': value, 'start_date': start_week.strftime(DF),
                     'last_date': end_week.strftime(DF)})

        return [{'values': data}]

    @api.one
    def _kanban_dashboard_graph_contract(self):
        self.kanban_dashboard_graph_contract = json.dumps(self.get_bar_graph_datas())

    @api.multi
    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        action['domain'] = [('flow', '=', self.name)]
        return action

    @api.multi
    def open_action(self):
        return self._get_action('l10n_cu_hlg_contract.contract_action_type')
