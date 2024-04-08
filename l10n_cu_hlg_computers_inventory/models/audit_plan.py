# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from datetime import  date


class AuditPlan(models.Model):
    _name = 'computers_inventory.audit_plan'
    _inherit = 'mail.thread'
    _description = 'audit_plan'

    name = fields.Char(string='Audit', default='Audit')

    department_id = fields.Many2one('hr.department', 'Area', required=True)

    @api.model
    def _default_month(self):
        fecha = date.today()
        fecha = str(fecha).split('-')
        return fecha[1]

    @api.model
    def _default_year(self):
        fecha = date.today()
        fecha_list = str(fecha).split('-')
        return fecha_list[0]

    def default_year(self):
        fecha = str(date.today()).split('-')
        year_list = []
        for i in range(int(fecha[0]) - 2, int(fecha[0]) + 5):
            tuple = (str(i), str(i))
            year_list.append(tuple)
        return year_list

    month = fields.Selection(
        [('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December')], required=True, string='Month', default=_default_month)

    year = fields.Selection(default_year, string="Year", required=True, track_visibility='onchange', default=_default_year)

    cause = fields.Text('Cause', track_visibility='onchange', required=True)
    state = fields.Selection([('planned', 'Planned'), ('approved', 'Approved'), ('done', 'Done'), ('unrealized', 'Unrealized')], 'Status', readonly=True,
                             copy=False, default='planned', track_visibility='onchange',
                             help='Initially the audits are created as "Planned", and their status can be changed to "Approved". Once the audit is approved, we can change its status to "Done" or "Unrealized" depending on the case.')

    
    @api.one
    def button_planned(self):
        self.state = 'planned'

    @api.one
    def button_approved(self):
        self.state = 'approved'

    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def button_unrealized(self):
        self.state = 'unrealized'

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state != 'planned':
                raise UserError(_("Unlink in state planned."))
        return super(AuditPlan, self).unlink()

