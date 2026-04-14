# -*- coding: utf-8 -*-

from odoo import models, fields

class HrCurriculum(models.Model):
    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"
   
    _inherit = 'ir.needaction_mixin'

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    category = fields.Selection([('professional', 'Professional'),
                                 ('academic', 'Academic'),
                                 ('certification', 'Certification'),
								 ('scientific', 'Scientific'),
								 ('teacher', 'Teacher'),
                                 ('professions','Professions')],
                                'Category',
                                required=True,
                                default='professional',
                                help='Category')
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Employer, School, University, "
                                      "Certification Authority")
    