from odoo import api, fields, models

class MembersGroups(models.Model):
    _name = 'calendar_turei.members_groups'
    _description = 'calendar_turei.members_groups'

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True)
    job_id = fields.Many2one('hr.job', string='Puesto de trabajo', related='employee_id.job_id')
    membership_type_id = fields.Many2one('calendar_turei.membership_type', string='Tipo membresía', required=True)
    organizational_groups_id = fields.Many2one('calendar_turei.organizational_groups')