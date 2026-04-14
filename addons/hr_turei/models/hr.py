# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _
import datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    smoker = fields.Boolean('Smoker', required=True, default=False)
    brand_smoke_id = fields.Many2one('hr_sgp_integration.brand', string='Smoking brand')
    carries_daily_smoking = fields.Boolean(string='Carries Daily smoking')
    packs_amount = fields.Selection([('1', '1'), ('2', '2')], string='Packs Amount', default='1')
    incentive = fields.Boolean(string='Carries Productivity Incentive', required=True, default=False)
    smoking_prod_incentive_context = fields.Selection([('module', 'Module'), ('turn', 'Turn'), ('ueb', 'UEB')], string='Productive Icentive Evaluation Context')
    smoking_prod_incentive_plan_type = fields.Selection([('rrhh', 'Sobre cumplimiento plan RRHH'), ('ptrc', 'Sobre cumplimiento PTRC'), ('hebra', 'Sobre cumplimiento producción HEBRA')], string='Overcompliance plan type')
    smoking_prod_incentive_reject = fields.Boolean('Take into account rejection', default=True)

    @api.model
    def create(self, values):
        creating = super(HrEmployee, self).create(values)
        if values['job_id']:
            values_for_movement = {'employee_code': values['code'],
                                   'employee_id': creating.id,
                                   'new_job_position_id': values['job_id'],
                                   'old_job_position_id': False,
                                   'movement_type': 'R',
                                   'movement_start_date': values['admission_date'],
                                   'company_id': values['company_id']}
            self.env['hr_turei.employee_movement'].create(values_for_movement)
        return creating

    def write(self, values):
        if 'active' in values and not self._context.get('no_create_movement', False):
            for record in self:
                if record.job_id:
                    if not values['active']:
                        values_for_movement = {'employee_code': record.code,
                                               'employee_id': record.id,
                                               'old_job_position_id': record.job_id.id,
                                               'new_job_position_id': False,
                                               'movement_type': 'D',
                                               'movement_start_date': fields.Date.to_string(datetime.date.today()),
                                               'movement_end_date': fields.Date.to_string(datetime.date.today()),
                                               'company_id': record.company_id.id}
                    else:
                        values_for_movement = {'employee_code': record.code,
                                               'employee_id': record.id,
                                               'new_job_position_id': record.job_id.id,
                                               'old_job_position_id': False,
                                               'movement_type': 'R',
                                               'movement_start_date': fields.Date.to_string(datetime.date.today()),
                                               'company_id': record.company_id.id}

                    self.env['hr_turei.employee_movement'].create(values_for_movement)

        return super(HrEmployee, self).write(values)


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    smoking_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], required=True, default='internal', string='Smoking Type')
