# -*- coding: utf-8 -*-

from odoo.fields import Boolean
from odoo.models import Model


class Employee(Model):
    _inherit = 'hr.employee'
    can_authorize_a_request = Boolean(string='Can authorize a request?')
Employee()
