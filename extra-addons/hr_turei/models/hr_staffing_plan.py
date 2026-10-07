from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrStaffingPlan(models.Model):
    _name = 'hr.staffing.plan'
    _description = 'Staffing Plan'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, id desc'

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
    )
    date_from = fields.Date(
        string='Start Date',
        required=True,
        tracking=True,
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        related='company_id.currency_id',
        store=True,
        string='Currency',
    )
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        help='Root department of the plan. If empty, it applies to the entire company.',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )
    line_ids = fields.One2many(
        comodel_name='hr.staffing.plan.line',
        inverse_name='plan_id',
        string='Plan Lines',
        copy=True,
    )
    total_approved_headcount = fields.Integer(
        string='Total Approved Headcount',
        compute='_compute_totals',
        store=True,
    )
    total_monthly_salary = fields.Monetary(
        string='Total Monthly Salary',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id',
    )
    notes = fields.Text(string='Notes')

    @api.depends('line_ids.approved_headcount', 'line_ids.subtotal')
    def _compute_totals(self):
        for plan in self:
            plan.total_approved_headcount = sum(plan.line_ids.mapped('approved_headcount'))
            plan.total_monthly_salary = sum(plan.line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.staffing.plan') or 'New'
        return super().create(vals_list)

    def action_submit(self):
        for plan in self:
            if not plan.line_ids:
                raise UserError(_('You cannot submit a plan without lines.'))
            plan.state = 'submitted'

    def action_approve(self):
        for plan in self:
            if not plan.line_ids:
                raise UserError(_('You cannot approve a plan without lines.'))
        self.write({'state': 'approved'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})