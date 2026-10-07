from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrStaffingPlanLine(models.Model):
    _name = 'hr.staffing.plan.line'
    _description = 'Staffing Plan Line'

    plan_id = fields.Many2one(
        comodel_name='hr.staffing.plan',
        string='Plan',
        required=True,
        ondelete='cascade',
    )
    plan_state = fields.Selection(
        string='Plan Status',
        related='plan_id.state',
    )
    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job Position',
        required=True,
        ondelete='restrict',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        related='job_id.department_id',
        store=True,
        readonly=True,
    )
    scale_group = fields.Char(
        string='Scale Group',
        required=True,
        help='Approved Scale Group (e.g. XVI, XX, XXII).',
    )
    salary = fields.Monetary(
        string='Salary',
        currency_field='currency_id',
        required=True,
        help='Monthly salary approved for the position according to the staffing plan.',
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='plan_id.currency_id',
        string='Currency',
    )
    occupational_category = fields.Char(
        string='Occupational Category',
        required=True,
        help='Approved Occupational Category (e.g. DINS, TNS, ONM, O, S).',
    )
    preparation_level = fields.Char(
        string='Preparation Level',
        required=True,
        help='Level of preparedness required in accordance with Annex 14.',
    )
    approved_headcount = fields.Integer(
        string='Approved Headcount',
        default=1,
        required=True,
        help='Number of approved positions for this role in the staffing plan.',
    )
    current_headcount = fields.Integer(
        string='Current Headcount',
        related='job_id.current_headcount',
    )
    vacant_headcount = fields.Integer(
        string='Vacant Headcount',
        related='job_id.vacant_headcount',
    )
    subtotal = fields.Monetary(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True,
        currency_field='currency_id',
    )

    _sql_constraints = [
        # Cada puesto debe aparecer una sola vez por plan.
        (
            'plan_job_unique',
            'UNIQUE(plan_id, job_id)',
            'This job position already exists in the plan. '
            'Each position can only appear once per plan.',
        ),
        # La plantilla aprobada debe ser positiva
        (
            'approved_headcount_positive',
            'CHECK(approved_headcount > 0)',
            'The approved headcount must be greater than zero.',
        ),
        # El salario no puede ser negativo
        (
            'salary_not_negative',
            'CHECK(salary >= 0)',
            'Salary cannot be negative.',
        ),
    ]

    @api.depends('salary', 'approved_headcount')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.salary * line.approved_headcount

    def action_open_recruitment(self):
        """
        Abre el reclutamiento para este puesto:
        - Solo si el plan está aprobado.
        - Solo si hay plazas vacantes.
        - Devuelve la acción del kanban de hr.applicant.
        """
        self.ensure_one()
        if self.plan_state != 'approved':
            raise UserError(_('The plan must be approved before opening recruitment.'))
        if self.vacant_headcount <= 0:
            raise UserError(_('There are no vacant positions to recruit for this job.'))
        return self.job_id.action_open_applicants()
