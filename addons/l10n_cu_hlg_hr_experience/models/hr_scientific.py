# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrScienceDegreeCategory(models.Model):
    _name = 'hr.science.degree.category'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)

    _sql_constraints = [
             ('name', 'unique (name)', 'The name must be unique!'),
             ('code', 'unique (code)', 'The code must be unique!')
         ]

class HrEmployeeScienceDegree(models.Model):
    _name = 'hr.employee.science.degree'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)

    science_degree_id = fields.Many2one('hr.science.degree.category', required=True)

    @api.model
    def create(self, vals):
        vals['category'] = 'scientific'
        return super(HrEmployeeScienceDegree, self).create(vals)