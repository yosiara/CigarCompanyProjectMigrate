from odoo import models, fields, api, _
import time
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class hr_turei_employee_movement_cause(models.Model):
    _name = 'hr_turei.employee_movement_cause'

    name = fields.Char(string='Cause', required=True)


class hr_turei_employee_movement(models.Model):
    _name = 'hr_turei.employee_movement'
    _rec_name = 'employee_id'
    _order = 'movement_start_date desc'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get('cmi.indicator')
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)

    employee_code = fields.Char(string='Code', required=True, index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, index=True)
    old_job_position_id = fields.Many2one('hr.job', string='Old Job Position')
    new_job_position_id = fields.Many2one('hr.job', string='New Job Position')
    movement_start_date = fields.Date(string='Movement Start Date', required=True,
                                      default=lambda *a: time.strftime('%Y-%m-%d'), index=True)
    movement_end_date = fields.Date(string='Movement End Date', index=True)
    movement_type = fields.Selection([('PR', 'Permanent Reallocation'), ('TR', 'Temporary Reallocation'),
                                      ('R', 'Register (Don\'t select)'), ('D', 'Discharge (Don\'t select)')],
                                     string='Movement Type', required=True)
    movement_cause = fields.Many2one('hr_turei.employee_movement_cause')


    @api.constrains('old_job_position_id', 'new_job_position_id')
    @api.one
    def _validate_job_positions(self):
        if not self.old_job_position_id and not self.new_job_position_id:
            raise UserError(_('The fields "Old Job Position" and "New Job Position" can not be empty '
                              'at the same time.'))
        if not self.new_job_position_id and self.movement_type == 'TR':
            raise UserError(_('The field "New Job Position" can not be empty for transitory movements'))
        if not self.new_job_position_id and self.movement_type == 'R':
            raise UserError(_('The field "New Job Position" can not be empty for register movements'))
        if not self.new_job_position_id and self.movement_type == 'PR':
            raise UserError(_('The field "New Job Position" can not be empty for permanent reallocation movements'))

    @api.onchange('employee_code')
    def _onchange_employee_code(self):
        if self.employee_code:
            obj_employee_id = self.env['hr.employee'].search([('code', '=', self.employee_code)])
            self.employee_id = obj_employee_id.id
            last_movement = self.search([('employee_id', '=', self.employee_id.id)], order='id DESC', limit=1)
            if last_movement is not None:
                self.old_job_position_id = last_movement.new_job_position_id
                self.old_contract_type = last_movement.new_contract_type
            else:
                raise UserError(_('These employee have not registered movements.'))

    @api.model
    def create(self, values):
        if values['movement_type'] == 'PR' or values['movement_type'] == 'D':
            last_movement = self.search([('employee_id', '=', values['employee_id']), ('movement_type', 'in', ['PR', 'A'])], order='movement_start_date DESC')
            last_date = fields.Date.from_string(values['movement_start_date']) - relativedelta(days=1)
            last_movement.write({'movement_end_date': fields.Date.to_string(last_date)})

        if values['movement_type'] == 'PR' or values['movement_type'] == 'A':
            job_data = self.env['hr.job'].search([('id', '=', values['new_job_position_id'])])
            employee_obj = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            values_employee = {'job_id': values['new_job_position_id'],
                               'department_id': job_data.department_id.id}
            employee_obj.write(values_employee, True)

        return super(hr_turei_employee_movement, self).create(values)

    @api.one
    def write(self, values):
        if values['movement_type'] == 'PR' or values['movement_type'] == 'A':
            job_data = self.env['hr.job'].search([('id', '=', values['new_job_position_id'])])
            employee_obj = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
            values_employee = {'job_id': values['new_job_position_id'],
                               'department_id': job_data.department_id.id}
            employee_obj.write(values_employee, 'hr_turei.employee_movement')
        return super(hr_turei_employee_movement, self).write(values)
