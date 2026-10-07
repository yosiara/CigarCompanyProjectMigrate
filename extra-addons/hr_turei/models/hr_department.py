from odoo import api, models, fields, _

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    # Identificador único
    code = fields.Char(
        string='Code',
        copy=False,
        index=True,
        help='Unique department code. Used for bulk import and reporting.',
    )

    _sql_constraints = [
        (
            'code_unique',
            'UNIQUE(code)',
            'The department code must be unique.',
        ),
    ]