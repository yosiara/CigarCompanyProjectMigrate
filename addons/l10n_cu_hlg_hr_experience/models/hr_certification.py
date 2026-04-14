# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrCertification(models.Model):
    _name = 'hr.certification'
    _inherits = {'hr.curriculum': 'curriculum_id'}

    curriculum_id = fields.Many2one(
        'hr.curriculum', 'Curriculum',
        auto_join=True, index=True, ondelete="cascade", required=True)

    name = fields.Char('Name', required=True)

    certification = fields.Char('Certification Number',  help='Certification Number')

    @api.model
    def create(self, vals):
        vals['category'] = 'certification'
        return super(HrCertification, self).create(vals)
