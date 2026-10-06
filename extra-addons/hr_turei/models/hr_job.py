from odoo import fields, models, api, _
from odoo.exceptions import UserError

class HrJob(models.Model):
    _inherit = 'hr.job'

    # -------------------------------------------------------------------------
    # Historial de planes de dotación
    # -------------------------------------------------------------------------
    plan_line_ids = fields.One2many(
        comodel_name='hr.staffing.plan.line',
        inverse_name='job_id',
        string='Staffing Plan History',
    )

    # Puntero a la línea vigente (último plan aprobado)
    current_plan_line_id = fields.Many2one(
        comodel_name='hr.staffing.plan.line',
        string='Current Plan Line',
        compute='_compute_current_plan_line',
        store=True,
        help='Línea del plan más reciente aprobado para este puesto.',
    )
    current_plan_id = fields.Many2one(
        comodel_name='hr.staffing.plan',
        string='Current Plan',
        related='current_plan_line_id.plan_id',
        store=True,
    )

    @api.depends(
        'plan_line_ids',
        'plan_line_ids.plan_id.state',
        'plan_line_ids.plan_id.date_from',
    )
    def _compute_current_plan_line(self):
        for job in self:
            approved_lines = job.plan_line_ids.filtered(
                lambda line: line.plan_id.state == 'approved'
            )
            job.current_plan_line_id = approved_lines.sorted(
                key=lambda line: (line.plan_id.date_from, line.id),
                reverse=True,
            )[:1]

    # -------------------------------------------------------------------------
    # Campos del Anexo 14 - Plantilla de Cargo y Ocupaciones
    # -------------------------------------------------------------------------
    scale_group = fields.Char(
        string='Scale Group',
        related='current_plan_line_id.scale_group',
        store=True,
    )
    salary = fields.Monetary(
        string='Salary',
        currency_field='currency_id',
        related='current_plan_line_id.salary',
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        string='Currency',
    )
    occupational_category = fields.Char(
        string='Occupational Category',
        related='current_plan_line_id.occupational_category',
        store=True,
    )
    preparation_level = fields.Char(
        string='Preparation Level',
        related='current_plan_line_id.preparation_level',
        store=True,
    )
    approved_headcount = fields.Integer(
        string='Approved Headcount',
        related='current_plan_line_id.approved_headcount',
        store=True,
    )

    # -------------------------------------------------------------------------
    # Estado real del puesto
    # -------------------------------------------------------------------------
    current_headcount = fields.Integer(
        string='Current Headcount',
        compute='_compute_headcount',
        store=True,
        help='Cantidad de empleados activos actualmente en este puesto.',
    )
    vacant_headcount = fields.Integer(
        string='Vacant Headcount',
        compute='_compute_headcount',
        store=True,
        help='Plazas aprobadas menos plazas ocupadas. Nunca es negativo.',
    )
    no_of_recruitment = fields.Integer(
        string='Target',
        compute='_compute_headcount',
        store=True,
        copy=False,
        help='Number of new employees you expect to recruit.',
    )

    @api.depends(
        'approved_headcount',
        'employee_ids',
        'employee_ids.active',
        'application_ids',
        'application_ids.active',
        'application_ids.employee_id',
        'application_ids.stage_id.hired_stage',
    )
    def _compute_headcount(self):
        for job in self:
            job.current_headcount = len(job.employee_ids.filtered('active'))
            # Candidatos ya contratados cuyo empleado aún no se ha creado.
            hired_pending = len(job.application_ids.filtered(
                lambda a: a.active and a.stage_id.hired_stage and not a.employee_id
            ))
            job.vacant_headcount = max(
                job.approved_headcount - job.current_headcount - hired_pending,
                0,
            )
            job.no_of_recruitment = job.vacant_headcount

    def _check_vacant_position(self, additional=1):
        """
        Validación y chequeo de plazas para el puesto.
        """
        self.ensure_one()
        # Si la validación está desactivada, no bloquea.
        if not self.env.company.staffing_plan_enforced:
            return
        # Los usuarios con el grupo de excepción saltan la validación.
        if self.env.user.has_group('hr_turei.group_hr_staffing_override'):
            return
        # Sin plan aprobado no hay plazas.
        if not self.current_plan_line_id:
            raise UserError(_(
                'No approved staffing plan for "%s". '
                'Approve a plan before hiring for this position.',
                self.name,
            ))
        # Verificar que haya suficientes plazas vacantes.
        if self.vacant_headcount < additional:
            raise UserError(_(
                'Not enough vacant positions for "%(job)s". '
                'Approved: %(approved)s, Occupied: %(current)s, '
                'Requested: %(requested)s.',
                job=self.name,
                approved=self.approved_headcount,
                current=self.current_headcount,
                requested=additional,
            ))

    @api.model
    def _generate_code(self):
        """
        Genera un código con prefijo del departamento y secuencia de 3 dígitos.
        Ej: DG-001, LOG-005, PROD-B1-012.
        Si no hay departamento, usa 'GEN'.
        """
        self.ensure_one()
        prefix = self.department_id.code or 'GEN'
        pattern = f'{prefix}-%'
        last = self.search(
            [('code', '=like', pattern)],
            order='code desc',
            limit=1,
        )
        if last:
            try:
                last_num = int(last.code.rsplit('-', 1)[-1])
            except ValueError:
                last_num = 0
        else:
            last_num = 0
        return f'{prefix}-{last_num + 1:03d}'
  
    # Identificador único
    code = fields.Char(
        string='Code',
        # default=_generate_code,
        copy=False,
        readonly=False,
        index=True,
        help='Código único del puesto. Se usa para importación masiva y reportes.',
    )

    _sql_constraints = [
        (
            'code_unique',
            'UNIQUE(code)',
            'The job code must be unique.',
        ),
    ]

    def action_open_applicants(self):
        """ Abre el kanban de candidatos filtrado por este puesto. """
        self.ensure_one()
        return {
            'name': _('Applicants'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.applicant',
            'view_mode': 'kanban,list,form',
            'domain': [('job_id', '=', self.id)],
            'context': {
                'default_job_id': self.id,
                'search_default_job_id': self.id,
            },
            'target': 'current',
        }