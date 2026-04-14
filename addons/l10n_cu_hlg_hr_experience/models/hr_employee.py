# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    academic_ids = fields.One2many('hr.academic',
                                   'employee_id',
                                   'Academic experiences',
                                   help="Academic experiences")

    certification_ids = fields.One2many('hr.certification',
                                        'employee_id',
                                        'Certifications',
                                        help="Certifications")
    experience_ids = fields.One2many('hr.experience',
                                     'employee_id',
                                     'Professional Experiences',
                                     help='Professional Experiences')

    scientific_ids = fields.One2many('hr.employee.science.degree',
                                     'employee_id',
                                     'Scientific grade',
                                     help='Scientific grade')

    teacher_ids = fields.One2many('hr.employee.teaching',
                                     'employee_id',
                                     'Teaching category',
                                     help='Teaching category')

    profession_ids = fields.One2many('hr.employee.professions',
                                  'employee_id',
                                  'Professions',
                                  help='Professions')

