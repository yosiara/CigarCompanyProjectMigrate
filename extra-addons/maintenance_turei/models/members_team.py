from odoo import api, fields, models, tools, _

class MembersTeam(models.Model):
    _name = "maintenance_turei.members.team"
    _description = 'Members Team'

    member_id = fields.Many2one('hr.employee', string='Miembro')
    responsible = fields.Boolean('¿Es el Jefe de Brigada?')
    member_team_id = fields.Many2one(comodel_name="maintenance.team", string="Documento", required=False)