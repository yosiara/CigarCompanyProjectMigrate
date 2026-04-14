# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class Departments(models.Model):
    _name = 'cmi_turei.department'
    _description = 'Departments'

    name = fields.Char('Name', required=True)


class Indicator(models.Model):
    _inherit = 'cmi.indicator'

    department_id = fields.Many2one('cmi_turei.department', 'Department')



