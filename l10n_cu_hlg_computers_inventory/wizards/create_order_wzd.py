# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from odoo import models, fields, api


class CreateOrderWZD(models.TransientModel):
    _name = "computers_inventory.create_order_wzd"

    number = fields.Char('Number', required=True)

    #@api.multi
    def create_order(self):
        mr = self.env['maintenance.request'].search([('id', '=', self._context.get('active_id'))], limit=1)
        if mr:
            order = self.env['computers_inventory.work_order'].create({
                'number': self.number,
                'request_date': mr.request_date,
                'maintenance_request_id': mr.id
            })

            return {
                'type': 'ir.actions.act_window',
                'res_model': 'computers_inventory.work_order',
                'view_mode': 'form',
                'target': 'current',
                'res_id': order.id,
                'flags': {'initial_mode': 'edit'}
            }
