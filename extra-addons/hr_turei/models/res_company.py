from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    reup_number = fields.Char(
        string='REUP Number',
        help='Número de Registro Único de Entidades (REUP).',
    )
    organism = fields.Char(
        string='Organism',
        help='Organismo superior (ej. MINAGRI).',
    )
    national_entity = fields.Char(
        string='National Entity',
        help='Entidad nacional a la que pertenece (ej. Grupo TABACUBA).',
    )
    staffing_plan_enforced = fields.Boolean(
        string='Enforce Staffing Plan',
        default=False,
        help='Si está activo, no se puede contratar ni asignar un empleado '
             'a un puesto sin plazas vacantes aprobadas en un plan vigente.',
    )