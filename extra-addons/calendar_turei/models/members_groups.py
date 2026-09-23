from odoo import api, fields, models

class MembersGroups(models.Model):
    _name = 'calendar_turei.members_groups'
    _description = 'Members Groups'

    name = fields.Char(string='Name', related='employee_id.name', store=True)
    employee_id = fields.Many2one(
        comodel_name='hr.employee', 
        string='Employee *', 
        required=True, 
    )
    job_id = fields.Many2one(
        comodel_name='hr.job', 
        string='Job Position', 
        related='employee_id.job_id', 
        store=True, 
    )
    membership_type_id = fields.Many2one(
        comodel_name='calendar_turei.membership_type', 
        string='Membership Type *', 
        required=True, 
    )
    organizational_groups_id = fields.Many2one(
        comodel_name='calendar_turei.organizational_groups',
        string='Organizational Group',
    )