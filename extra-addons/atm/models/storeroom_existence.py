# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api


class StoreroomExistence(models.Model):
    _name = 'atm.storeroom_existence'
    _description = 'atm.storeroom_existence'
    _rec_name = 'date'
    _order = 'date desc'

    @api.model
    def _default_record_ids(self):
        fecha_last_day = datetime.datetime.now().date() - datetime.timedelta(days=1)
        return [(0, 0, {'storeroom_existence_id':self.id,'group_product': s,'quantity_last_day':self.env['atm.storeroom_product'].search([('group_product','=',s),('date','=',fecha_last_day)], order='date desc', limit=1).quantity, 'quantity':0.0}) for s in
            xrange(1,75)]

    date = fields.Date(default=fields.Date.today)
    record_ids = fields.One2many('atm.storeroom_product', inverse_name='storeroom_existence_id', string='Products', default=_default_record_ids)

    @api.onchange('date')
    def _onchange_date(self):
        for a in self.record_ids:
            fecha_last_day = datetime.date(int(self.date.split('-')[0]),int(self.date.split('-')[1]),int(self.date.split('-')[2])) - datetime.timedelta(days=1)
            last = a.search([('group_product', '=', a.group_product), ('date', '=', fecha_last_day)])
            a.quantity_last_day = last.quantity


class StoreroomProduct(models.Model):
    _name = 'atm.storeroom_product'
    _description = 'atm.storeroom_product'

    storeroom_existence_id = fields.Many2one('atm.storeroom_existence', string='Storeroom Existence')

    date = fields.Date(compute='_compute_date', store=True)
    group_product = fields.Integer()
    quantity_last_day = fields.Float(required=True, digits=(16, 4), string='Ultima cantidad', readonly=True)
    quantity = fields.Float(required=True, digits=(16, 4), string='Cantidad actual')

    
    @api.depends('storeroom_existence_id.date')
    def _compute_date(self):
        self.date = self.storeroom_existence_id.date


    @api.onchange('group_product')
    def _onchange_group_product(self):
        if self.group_product:
            last = self.search([('group_product', '=', self.group_product), ('date', '<', self.storeroom_existence_id.date)], order='date desc', limit=1)
            self.quantity_last_day = last.quantity

