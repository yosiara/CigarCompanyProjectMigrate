# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, fields, api

class ProductiveSectionPlan(models.Model):
    _name = 'process_control.productive_section_plan'
    _description = 'Productive Section Plan'

    def _default_year(self):
        date = str(fields.Datetime.now())
        return datetime.strptime(date.split('-')[0], '%Y').year

    name = fields.Char(string='Name *', required=True, default='Plan ')
    year = fields.Char(string='Year *', required=True, default=_default_year)
    activate = fields.Boolean(string='Active', default=True)
    productive_capacity = fields.Integer('Productive Capacity *', required=True)
    quantity_line = fields.Integer('Number of Lines *', required=True)
    productive_section_ids = fields.One2many('process_control.productive_section', 'productive_section_plan_id', 'Productive Section')

    # Indexes
    indice_planif_efici_real = fields.Float(string='Efficiency Index (%) *', required=True, default=0.00)
    indice_planif_rejection = fields.Float(string='Rejection Index (%) *', required=True, default=0.00)
    indice_planif_disp_tec = fields.Float(string='Technical Availability Index (%) *', required=True, default=0.00)
    indice_planif_norma = fields.Float(string='Plan Standard Index *', required=True, default=0.00)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The name of the Work Plan must be unique!'),
    ]

