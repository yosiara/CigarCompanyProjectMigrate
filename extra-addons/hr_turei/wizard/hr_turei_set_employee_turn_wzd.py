# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiSetEmployeeTurnWzd(models.TransientModel):
    _name = 'hr_turei.set_employee_turn_wzd'

    employee_ids = fields.Many2many('hr.employee', 'hr_turei_set_employee_shift_wzd_employee_rel', 'wizard_id', 'employee_id', 'Employees', required=True)
    calendar_id = fields.Many2one('resource.calendar', 'Turn', required=True)

    def execute(self):
        self.employee_ids.write({'calendar_id': self.calendar_id.id})
        return True
