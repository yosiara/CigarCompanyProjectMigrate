# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrTitles(models.Model):
    _name = 'hr.academic.titles'

    name = fields.Char('Name', required=True)

class HrAcademic(models.Model):
    _name = 'hr.academic'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)
    title_id = fields.Many2one('hr.academic.titles', required=True)

    tome = fields.Char('Tome', size=15, required=True)
    folio = fields.Char('Folio', size=15, required=True)
    registration_date = fields.Date('Registration date')
    principal = fields.Boolean('Principal')

    @api.model
    def create(self, vals):
        vals['category'] = 'academic'
        return super(HrAcademic, self).create(vals)
