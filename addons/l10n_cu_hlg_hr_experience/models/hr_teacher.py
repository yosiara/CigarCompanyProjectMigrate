# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrTeachingCategory(models.Model):
    _name = 'hr.teaching.category'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)

    _sql_constraints = [
             ('name', 'unique (name)', 'The name must be unique!'),
             ('code', 'unique (code)', 'The code must be unique!')
         ]

class HrEmployeeTeaching(models.Model):
    _name = 'hr.employee.teaching'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)

    teaching_id = fields.Many2one('hr.teaching.category', required=True)

    @api.model
    def create(self, vals):
        vals['category'] = 'teacher'
        return super(HrEmployeeTeaching, self).create(vals)