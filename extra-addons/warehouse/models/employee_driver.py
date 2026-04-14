# -*- coding: utf-8 -*-

from odoo import api, fields, tools, models


class EmployeeDriver(models.Model):
    _name = 'warehouse.employee_driver'
    _description = 'Employee Driver'

    name = fields.Char(required=True, string='Nombre y Apellidos')
    ci = fields.Char(string='Carnet Identidad')