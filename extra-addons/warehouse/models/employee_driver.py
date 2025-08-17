# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo import api, fields, tools


class EmployeeDriver(Model):
    _name = 'warehouse.employee_driver'

    name = fields.Char(required=True, string='Nombre y Apellidos')
    ci = fields.Char(string='Carnet Identidad')

EmployeeDriver()
