from odoo import api, fields, models

class OrganizationalGroups(models.Model):
    _name = 'calendar_turei.organizational_groups'
    _description = 'calendar_turei.organizational_groups'

    name = fields.Char(string='Nombre', required=True)
    members_groups_ids = fields.One2many('calendar_turei.members_groups', 'organizational_groups_id', string='Integrantes', required=True)