# -*- coding: utf-8 -*-

import datetime
from odoo import api
from odoo.models import Model
from odoo.fields import Many2one, Float, Date, One2many, Boolean


class CostCenterBudget(Model):
    _name = 'atm.cost_center.budget'
    _description = 'atm.cost_center.budget'
    _rec_name = 'cost_center_id'

    
    def _compute_real(self):
        work_order_type_obj = self.env['atm.work_order.type']
        used_in_budget = work_order_type_obj.search([('is_used_in_budget', '=', True)])

        request_obj = self.env['warehouse.warehouse_request']
        requests = request_obj.search([('cost_center_id', '=', self.cost_center_id.id),
                                       ('work_order_id.type_id.name', 'in', [x.name for x in used_in_budget])])

        first_day_current_year = datetime.datetime.now().strftime('%Y-01-01')
        last_day_current_year = datetime.datetime.now().strftime('%Y-12-31')
        requests = requests.filtered(lambda rec: first_day_current_year <= rec.date <= last_day_current_year)

        res = 0.0
        for request in requests:
            for requested_product in request.requested_product_ids:
                res += requested_product.product_id.price * requested_product.quantity
                res += requested_product.product_id.price_extra * requested_product.quantity

        self.real = res

    date = Date()
    cost_center_id = Many2one('l10n_cu_base.cost_center', string='Cost Center', required=True)
    real = Float(digits=(16, 4), compute=_compute_real)
    plan = Float(digits=(16, 4))
CostCenterBudget()


class CostCenter(Model):
    _inherit = 'l10n_cu_base.cost_center'

    
    def _compute_has_budgets(self):
        if not len(self.budget_ids):
            self.has_budgets = False
        self.has_budgets = True

    budget_ids = One2many('atm.cost_center.budget', inverse_name='cost_center_id', string='Correlated budgets...')
    has_budgets = Boolean(string='Has budgets?', compute=_compute_has_budgets)

    def is_budget_exceeded(self):
        first_day_current_year = datetime.datetime.now().strftime('%Y-01-01')
        last_day_current_year = datetime.datetime.now().strftime('%Y-12-31')
        today_budget = self.budget_ids.filtered(lambda rec: first_day_current_year <= rec.date <= last_day_current_year)
        return True if len(today_budget) and today_budget[0].real > today_budget[0].plan else False
CostCenter()
