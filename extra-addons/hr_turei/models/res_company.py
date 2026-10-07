from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    reup_number = fields.Char(
        string='REUP Number',
        help='Unique Entity Registration Number (REUP).',
    )
    organism = fields.Char(
        string='Organism',
        help='Higher organization (e.g. MINAGRI).',
    )
    national_entity = fields.Char(
        string='National Entity',
        help='National entity to which it belongs (e.g. TABACUBA Group).',
    )
    staffing_plan_enforced = fields.Boolean(
        string='Enforce Staffing Plan',
        default=False,
        help='If active, an employee cannot be hired or assigned to a position without approved vacancies in a current plan.'
    )