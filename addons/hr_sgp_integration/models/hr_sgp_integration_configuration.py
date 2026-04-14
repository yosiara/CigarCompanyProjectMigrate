# -*- coding: utf8 -*-

from odoo import models, fields, api, _


class Turn(models.Model):
    _name = 'hr_sgp_integration.turn'
    _description = "Turns configuration"
    _rec_name = 'sgp_name'

    sgp_id = fields.Integer(string='SGP identifier')
    sgp_name = fields.Char(string='SGP Name')
    active = fields.Boolean(string='Active', default=True)


class Module(models.Model):
    _name = 'hr_sgp_integration.module'
    _description = "Modules configuration"
    _rec_name = 'sgp_name'
    _order = 'sgp_id'

    sgp_id = fields.Integer(string='SGP Identifier')
    sgp_name = fields.Char(string='SGP Name')
    department_ids = fields.Many2many('hr.department', 'hr_sgp_integration_department_module_rel', 'module_id', 'department_id',
                                      string='Related Departments')
    active = fields.Boolean(string='Active', default=True)


class Brigade(models.Model):
    _name = 'hr_sgp_integration.brigade'
    _description = "Brigades configuration"
    _rec_name = 'sgp_name'

    sgp_id = fields.Integer(string='SGP Identifier')
    sgp_name = fields.Char(string='SGP Name')


class Materials(models.Model):
    _name = 'hr_sgp_integration.materials'
    _description = "Materials configuration"
    _rec_name = 'sgp_name'

    sgp_id = fields.Integer(string='SGP Identifier')
    sgp_name = fields.Char(string='SGP Name')
    active = fields.Boolean(string='Active', default=True)


class Brand(models.Model):
    _name = 'hr_sgp_integration.brand'
    _description = u'Brand configuration'
    _rec_name = 'sgp_name'

    sgp_id = fields.Integer(string='SGP Identifier')
    sgp_name = fields.Char(string='SGP Name')
    active = fields.Boolean(string='Active', default=True)




