# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import Warning

MESES =[('1','Enero'),
            ('2','Febrero'),
            ('3','Marzo'),
            ('4','Abril'),
            ('5','Mayo'),
            ('6','Junio'),
            ('7','Julio'),
            ('8','Agosto'),
            ('9','Septiembre'),
            ('10','Octubre'),
            ('11','Noviembre'),
            ('12','Diciembre'),]

class ReportRegistrationAttendanceWzd(models.TransientModel):
    _name = 'report.registration_attendance.wzd'
    _description = 'Registration of attendance'

    year = fields.Integer( string='Año',required=True, default=datetime.now().year)
    mes = fields.Selection( MESES, string='Mes',required=True, default=str(datetime.now().month))
    department_id = fields.Many2one('hr.department', 'Department')
    employee_ids = fields.Many2many('hr.employee', 'employee_registration_attendance_report_rel', 'report_id', 'employee_id', 'Employees')
    shows_sat_sun = fields.Boolean(default=True, string='It shows Saturdays and Sundays')

    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id:
            self.employee_ids = []
            # employee_ids = self.env['hr.employee'].sudo().search([('department_id', '=', self.department_id.id)], order='code')
            # self.employee_ids = [(6, 0, employee_ids.ids)]


    @api.multi
    def print_report(self):
        context = {}
        datas = {}
        ids_to_print = []
        if self.employee_ids:
            ids_to_print = self.employee_ids.ids
        else:
            raise Warning('Debe seleccionar al menos un empleado')

        data = self.read(['year','mes','shows_sat_sun'])[0]

        datas = {
                 'ids': ids_to_print,
                 'model': 'report.registration_attendance.wzd',
                 'form': data,
                 'context':context
        }
        
        return self.env['report'].get_action([], 'l10n_cu_hlg_hr.report_registration_attendance', data=datas)


