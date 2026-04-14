
from odoo import models, fields, api

class HrProfessions(models.Model):
    _name = 'hr.professions'

    name = fields.Char('Name', required=True)

    _sql_constraints = [
             ('name', 'unique (name)', 'The name must be unique!')
         ]

class HrEmployeeProfessions(models.Model):
    _name = 'hr.employee.professions'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)

    profession_id = fields.Many2one('hr.professions', required=True)

    @api.model
    def create(self, vals):
        vals['category'] = 'professions'
        return super(HrEmployeeProfessions, self).create(vals)