# -*- coding:utf-8 -*-

from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _compute_father(self):
        if self.id:
            family = self.env['hr.employee.family'].search(
                [('kindred', '=', 'father'),('employee_id', '=', self.id)])
            if family:
                self.father = family.name

    @api.one
    def _compute_mother(self):
        if self.id:
            family = self.env['hr.employee.family'].search(
                [('kindred', '=', 'mother'), ('employee_id', '=', self.id)])
            if family:
                self.mother = family.name

    @api.one
    def _compute_children(self):
        if self.id:
            family = self.env['hr.employee.family'].search(
                [('kindred', '=', 'son'), ('employee_id', '=', self.id)])
            if family:
                self.children = len(family.ids)

    family_ids = fields.One2many(
        string="Familys",
        comodel_name='hr.employee.family',
        inverse_name='employee_id'
    )
  
    father = fields.Char(compute='_compute_father', string="Father's Name")
    mother = fields.Char(compute='_compute_mother', string="Mother's Name")
    children = fields.Integer(compute='_compute_children', string='Number of Children')
