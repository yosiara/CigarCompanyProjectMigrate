# -*- coding: utf-8 -*-


from odoo import models, fields, api, osv
from datetime import *
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class WzdReportInspection(models.TransientModel):
    _name = "computers_inventory.report_inspection_wzd"

    start_date = fields.Date(string='Start date', required=True, default=date.today())
    end_date = fields.Date(string='End date', required=True, default=date.today())
    format = fields.Selection([('pdf', 'PDF'), ('docx', 'DOCX')], 'Format', default='pdf', required=True)
    elaborates_id = fields.Many2one('hr.employee', 'Elaborates', required=True)
    approved_id = fields.Many2one('hr.employee', 'Approved', required=True)

    @api.constrains('start_date', 'end_date')
    def _constraint_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('The start date can not be greater that end date.'))
        return True

    @api.multi
    def print_report(self):
        data = {}
        data['start_date'] = self.start_date
        data['end_date'] = self.end_date
        data['elaborates_id'] = self.elaborates_id.id
        data['approved_id'] = self.approved_id.id

        if self.format == 'pdf':
            return self.env['report'].get_action(self, 'l10n_cu_hlg_computers_inventory.report_inspection', data=data)
        else:
            return {
                        'type': 'ir.actions.report.xml',
                        'report_name': 'l10n_cu_hlg_computers_inventory.report_inspection_docx',
                        'datas': data
                    }