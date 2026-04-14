# -*- coding:utf-8 -*-

from odoo import models, fields

GENDER_SELECTION = [('male', 'Male'),
                    ('female', 'Female')]

KINDRED_SELECTION = [('mother', 'Mother'),
                    ('father', 'Father'),
                    ('son','Son'),
                    ('brother','Brother'),
                    ('spouse','Epouse'),
                    ('grandfather','Grandfather'),
                    ('cousin','Cousin'),
                    ('uncle','Uncle')
                    ]

class HrFamilys(models.Model):
    _name = 'hr.employee.family'
    _description = 'HR Employee famyly'

    employee_id = fields.Many2one( string="Employee", comodel_name='hr.employee')
    name = fields.Char(string="Name", required=True )
    date_of_birth = fields.Date(string="Date of Birth")
    kindred =  fields.Selection(
        string='kindred',
        selection=KINDRED_SELECTION
    )
    gender = fields.Selection(
        string='Gender',
        selection=GENDER_SELECTION
    )
    coexistence = fields.Boolean(string="Coexistence", default=True)
