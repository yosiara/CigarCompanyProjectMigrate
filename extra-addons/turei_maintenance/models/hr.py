# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class Employee(models.Model):
    _inherit = "hr.employee"

    employee_work_order_id = fields.Many2one(comodel_name="turei_maintenance.work_order", string="Documento",
                                             required=False)