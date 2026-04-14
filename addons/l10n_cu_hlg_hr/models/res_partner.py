# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    employee = fields.Boolean(compute='_compute_employee', store=True)
    employee_ids = fields.One2many('hr.employee', "address_home_id", "Employees", readonly=True, invisible=True)

    @api.one
    @api.depends('employee_ids.address_home_id')
    def _compute_employee(self):
        self.employee = True if len(self.employee_ids) else False
