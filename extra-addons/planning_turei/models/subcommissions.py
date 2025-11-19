from odoo import models, fields, api, _

class Subcommissions(models.Model):
    _name = 'planning_turei.subcommissions'
    _description = 'Planning Turei Subcommissions'

    name = fields.Char(string='Subcomisión', required=True)
    planning_role_id = fields.Many2one('planning.role', string='Comisión', required=True)