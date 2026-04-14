# -*- coding: utf-8 -*-

import datetime
from odoo import api
from odoo.models import Model
from odoo.fields import Char, Many2one, Boolean, One2many
from odoo.exceptions import UserError
from odoo.tools.translate import _


class WarehouseRequest(Model):
    _inherit = 'warehouse.warehouse_request'

    def _get_code(self):
        warehouse_requests = self.search([], limit=1, order='date DESC, code DESC')
        if not len(warehouse_requests):
            return '00001'

        temp = int(warehouse_requests[0].code)
        rep = str(temp + 1)
        code = ''

        for x in range(0, 5 - len(rep)):
            code += '0'

        code += rep
        return code

    @api.one
    def _is_cost_center_exceeding_budget(self):
        if self.cost_center_id.is_budget_exceeded():
            self.is_exceeded_budget = True
        else:
            self.is_exceeded_budget = False

    @api.one
    def _is_exceeded_product_assingment(self):
        print self.area_id.is_assingment_exceeded()
        if self.area_id.is_assingment_exceeded():
            self.is_exceeded_assingment = True
        else:
            self.is_exceeded_assingment = False

    code = Char(required=True, default=_get_code)
    work_order_id = Many2one('atmsys.work_order', string='Work order', domain=[('state', '=', 'open')])

    area_id = Many2one('l10n_cu_base.area', string='Area')
    responsibility_area_id = Many2one('l10n_cu_base.responsibility_area', string='Responsibility Area', required=True)
    cost_center_id = Many2one('l10n_cu_base.cost_center', string='Cost Center', required=True)

    # Used to alert when the budget value has been exceeded...
    is_exceeded_budget = Boolean(compute=_is_cost_center_exceeding_budget)

    # Used when the product assignment to the area has been exceeded...
    is_exceeded_assingment = Boolean(compute=_is_exceeded_product_assingment)

    # Used to generate user's advises on products request...
    warning_message = Char(compute='_compute_requested_products')

    required_field_receive_id = Boolean(compute='_compute_required_field_receive_id')

    @api.multi
    @api.depends('requested_product_ids')
    def _compute_required_field_receive_id(self):
        for rec in self:
            for x in rec.requested_product_ids:
                if x.product_id.account_id.code in [187, 240, 241, 242, 243, 244, 247, 248, 249, 250, 251]:
                    rec.required_field_receive_id = True
                    continue

    @api.one
    @api.depends('requested_product_ids')
    def _compute_requested_products(self):
        for product_order in self.requested_product_ids:
            product = product_order.product_id

            message = ''
            if product.is_protected:
                message += _('Product protected: ') + product.protection_cause + '. '

            if product.is_tool_or_util:
                message += _('Product is util or tool. ')

            if product.is_for_contingency:
                message += _('Product is for contingency. ')

            if product.do_not_use:
                message += _('This product is not for use. ')

            if product.is_exclusive_product:
                message += _('This product is for exclusive use to: ') + product.area_id.name + '. '

            if product.has_assingments:
                message += _('Este producto tiene asignaciones. Especifique el area para realizar la comprobacion... ')

            self.warning_message = message

    @api.onchange('work_order_id')
    def on_change_work_order(self):
        if self.work_order_id:
            self.responsibility_area_id = self.work_order_id.receive_cost_center_id.responsibility_area_id
            self.cost_center_id = self.work_order_id.receive_cost_center_id

    @api.model
    def create(self, values):
        res = super(WarehouseRequest, self).create(values)
        for rec in res.requested_product_ids:
            rec.write({'work_order_id': res.work_order_id.id})
        return res

    @api.multi
    def write(self, values):
        if self.work_order_id and self.work_order_id.state == 'closed':
            if values.get('requested_product_ids', False):
                for new_request in values['requested_product_ids']:
                    if new_request[0] == 0:
                        raise UserError(_('The associated Work Order is closed...'))

        res = super(WarehouseRequest, self).write(values)
        for rec in self.requested_product_ids:
            rec.write({'work_order_id': self.work_order_id.id})
        return res
WarehouseRequest()


class ProductOrder(Model):
    _inherit = 'warehouse.product_order'
    work_order_id = Many2one('atmsys.work_order', string='Work Order')
ProductOrder()


class Area(Model):
    _inherit = 'l10n_cu_base.area'

    @api.one
    def _compute_has_assingments(self):
        if not len(self.assingment_ids):
            self.has_assingments = False
        self.has_assingments = True

    has_assingments = Boolean(string='Has assingments?', compute=_compute_has_assingments)
    assingment_ids = One2many('atmsys.product_assignment', inverse_name='area_id', string='Assingments...')

    def is_assingment_exceeded(self):
        first_day_current_year = datetime.datetime.now().strftime('%Y-01-01')
        last_day_current_year = datetime.datetime.now().strftime('%Y-12-31')
        #today_assingment = self.assingment_ids.filtered(lambda rec: first_day_current_year <= rec.date <= last_day_current_year)
        today_assingment = self.assingment_ids.search([('date','>=', first_day_current_year),('date','<=',last_day_current_year), ('area_id','=', self.id)], order='date desc')
        #for t in today_assingment:
        #    print str(t.date) + "--" + str(t.quantity)
        #print today_assingment[0].given_quantity
        #print today_assingment[0].quantity
        return True if len(today_assingment) and today_assingment[0].given_quantity > today_assingment[0].quantity else False
Area()


class CostCenter(Model):
    _inherit = 'l10n_cu_base.cost_center'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        area = self.env.context.get('responsibility_area_id', False)
        if not area and self.env.context.get('restricted', False):
            return []

        if area and self.env.context.get('restricted', False):
            return self.search([('responsibility_area_id', '=', area)], limit=limit).name_get()

        return super(CostCenter, self).name_search(name, args, operator, limit)
CostCenter()
