# -*- coding: utf-8 -*-
import math
from odoo import api, fields, models


class RealizedWork(models.Model):
    _name = 'maintenance_turei.realized_work'
    _description = 'turei_maitenance.realized_work'

    executor_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    code_executor = fields.Char(string='Código', required=True)
    description = fields.Text(string='Trabajo')
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipo', required=True)
    type = fields.Selection([('cambio_pieza', 'Cambio de Pieza'), ('reparacion', 'Reparación'), ('ajustes','Ajustes'), ('otros','Otros')], string='Tipo')
    time = fields.Char(string='Tiempo(Hr)')
    time_hr = fields.Float('Tiempo(Hr)')
    ready_service = fields.Selection([('si', 'SI'), ('no', 'NO')], string='Servicio Concluido')
    note = fields.Text(string="Observaciones")
    realized_work_order_id = fields.Many2one(comodel_name="maintenance_turei.work_order", string="Documento", required=False)
    rate = fields.Float('Tarifa', compute='_compute_rate', store=True)

    @api.onchange('executor_id')
    def onchange_executor_id(self):
        if self.executor_id:
            self.code_executor = self.executor_id.code

    @api.depends('executor_id', 'time_hr')
    def _compute_rate(self):
        for record in self:
            if record.executor_id and record.time_hr:
                scale_salary = record.executor_id.job_id.salary_group_id.scale_salary
                record.rate = (scale_salary / 190.6) * record.time_hr
            else:
                record.rate = 0

    @api.onchange('code_executor')
    def onchange_code_executor(self):
        if self.code_executor:
            employee_id = self.env['hr.employee'].search([('code', '=', self.code_executor)])
            if employee_id:
                self.executor_id = employee_id.id
            else:
                self.executor_id = False

    def float_time_to_hour_minutes(self, float_time):
        time_values = math.modf(float_time)
        hours = int(time_values[1])
        minutes = round(time_values[0] * 60)
        return hours, minutes