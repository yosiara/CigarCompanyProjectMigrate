# # -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Department(models.Model):
    _inherit = 'hr.department'

    # turn_sgp_ids = fields.One2many('hr_sgp_integration.turn', 'department_id', string='Related departments in SGP')
    # module_sgp_ids = fields.One2many('hr_sgp_integration.module', 'department_id', string='Related departments in SGP')

