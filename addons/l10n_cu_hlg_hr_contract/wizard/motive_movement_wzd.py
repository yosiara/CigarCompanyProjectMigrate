# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MotiveMovementWzd(models.TransientModel):
    _name = 'motive.movement.wzd'

    supplement_description = fields.Many2one('hr_contract.supplement_motive',
                                             string='Supplement Motive', required=True)

    date_start = fields.Date('Start Date', required=True, default=fields.Date.today)

    @api.multi
    def btn_save(self):
        obj = self.browse(self._ids[0])

        context = self._context or {}

        id = context.get('contract_id')
        state = context.get('state')

        contract_obj = self.env['hr.contract']
        motive_id = obj.supplement_description.id
        date_start = obj.date_start
        contract = contract_obj.browse(id)

        result = contract.create_supplement(motive_id, date_start, state)

        return {}