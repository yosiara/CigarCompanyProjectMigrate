# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiSmokingAdditionalIncidencesWzd(models.TransientModel):
    _name = 'hr_turei.smoking_additional_incidences_wzd'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    employee_ids = fields.Many2many('hr.employee', 'hr_turei_employee_smoking_add_inc_wzd_rel', 'wizard_id', 'employee_id', string='Employees')
    external_staff_ids = fields.Many2many('hr_turei.external_staff', 'hr_turei_external_staff_smoking_add_inc_wzd_rel', 'wizard_id', 'external_staff_id', string='External Staff')
    concept_id = fields.Many2one('hr_turei.cigarette_concept', 'Concept', required=True)
    hours_amount = fields.Float(string='Hours Amount')
    packs = fields.Integer(string='Packs', required=True)
    cause = fields.Char(string='Cause')
    period_id = fields.Many2one('hr_turei.smoke_period', string='Period', domain=([('state', '=', 'open')]),
                                required=True)

    def execute(self):

        for employee in self.employee_ids:
            register = self.env['hr_turei.additional_incidences'].search(
                [('employee_id', '=', employee.id), ('period_id', '=', self.period_id.id)])
            if register:
                data = {
                    'concept_id': self.concept_id.id,
                    'hours_amount': self.hours_amount,
                    'packs': self.packs,
                    'cause': self.cause,
                    'additional_incidences_id': register.id
                }
                self.env['hr_turei.additional_incidences.line'].create(data)
            else:
                data = {
                    'concept_id': self.concept_id.id,
                    'hours_amount': self.hours_amount,
                    'packs': self.packs,
                    'cause': self.cause
                }
                self.env['hr_turei.additional_incidences'].create({
                    'company_id': self.company_id.id,
                    'employee': True,
                    'employee_id': employee.id,
                    'code': employee.code,
                    'period_id': self.period_id.id,
                    'line_ids': [(0, 0, data)]
                })

        for person in self.external_staff_ids:
            register = self.env['hr_turei.additional_incidences'].search(
                [('external_staff_id', '=', person.id), ('period_id', '=', self.period_id.id)])
            if register:
                data = {
                    'concept_id': self.concept_id.id,
                    'hours_amount': self.hours_amount,
                    'packs': self.packs,
                    'cause': self.cause,
                    'additional_incidences_id': register.id
                }
                self.env['hr_turei.additional_incidences.line'].create(data)
            else:
                data = {
                    'concept_id': self.concept_id.id,
                    'hours_amount': self.hours_amount,
                    'packs': self.packs,
                    'cause': self.cause
                }
                self.env['hr_turei.additional_incidences'].create({
                    'company_id': self.company_id.id,
                    'employee': False,
                    'external_staff_id': person.id,
                    'code': person.code,
                    'period_id': self.period_id.id,
                    'line_ids': [(0, 0, data)]
                })

        return True
