# -*- coding: utf-8 -*-

from odoo.models import Model
from odoo.fields import Char

class Department(Model):
    _inherit = "hr.department"
    external_id = Char('External Id')


class Job(Model):
    _inherit = "hr.job"
    external_id = Char('External Id')


class Employee(Model):
    _inherit = "hr.employee"
    external_id = Char('External Id')