# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiCreateEmployeeMovementsWzd(models.TransientModel):
    _name = 'hr_turei.create_employee_movements_wzd'

    def execute(self):
        for employee in self.env['hr.employee'].search([]):
            movements = self.env['hr_turei.employee_movement'].search(
                [('employee_id', '=', employee.id), '|', ('movement_type', '=', 'PR'), ('movement_type', '=', 'R')])
            if not movements and employee.job_id:
                self.env['hr_turei.employee_movement'].create({
                    'employee_code': employee.code,
                    'employee_id': employee.id,
                    'new_job_position_id': employee.job_id.id,
                    'old_job_position_id': False,
                    'movement_type': 'R',
                    'movement_start_date': employee.admission_date,
                    'company_id': employee.company_id.id
                })
        return True
