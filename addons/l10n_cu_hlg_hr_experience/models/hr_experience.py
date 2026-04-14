# -*- coding: utf-8 -*-

from odoo import models, fields

class HrExperience(models.Model):
    _name = 'hr.experience'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)
    name = fields.Char('Name', required=True)
