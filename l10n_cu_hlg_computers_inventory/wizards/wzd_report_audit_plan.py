# -*- coding: utf-8 -*-


from odoo import models, fields, api, osv
from datetime import *
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class AuditPlanWzd(models.TransientModel):
    _name = "computers_inventory.audit_plan_wzd"

    @api.model
    def _default_year(self):
        fecha = date.today()
        fecha_list = str(fecha).split('-')
        return fecha_list[0]

    def default_year(self):
        fecha = str(date.today()).split('-')
        year_list = []
        for i in range(int(fecha[0]) - 2, int(fecha[0]) + 20):
            tuple = (str(i), str(i))
            year_list.append(tuple)
        return year_list

    year = fields.Selection(default_year, string="Year", required=True, default=_default_year)
    elaborates_id = fields.Many2one('hr.employee', 'Elaborates', required=True)
    approved_id = fields.Many2one('hr.employee', 'Approved', required=True)

    @api.multi
    def print_report(self):
        data = {}
        data['year'] = self.year
        data['elaborates_id'] = self.elaborates_id.id
        data['approved_id'] = self.approved_id.id

        return self.env['report'].get_action(self, 'l10n_cu_hlg_computers_inventory.report_audit_plan', data=data)
