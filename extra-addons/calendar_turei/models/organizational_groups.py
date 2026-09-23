from odoo import api, fields, models

class OrganizationalGroups(models.Model):
    _name = 'calendar_turei.organizational_groups'
    _description = 'Organizational Groups'

    name = fields.Char(string='Name *', required=True)
    members_groups_ids = fields.One2many(
        comodel_name='calendar_turei.members_groups', 
        inverse_name='organizational_groups_id', 
        string='Members *', 
        required=True, 
    )