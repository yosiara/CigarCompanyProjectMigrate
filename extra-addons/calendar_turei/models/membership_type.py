from odoo import api, fields, models

class MembershipType(models.Model):
    _name = 'calendar_turei.membership_type'
    _description = 'Membership Type'

    name = fields.Char(string='Name *', required=True)