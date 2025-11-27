from odoo import api, fields, models

class MembershipType(models.Model):
    _name = 'calendar_turei.membership_type'
    _description = 'calendar_turei.membership_type'

    name = fields.Char(string='Membresía', required=True)