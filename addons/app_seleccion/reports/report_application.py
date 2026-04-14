# -*- coding: utf-8 -*-
from odoo import api, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class ReportApplication(models.AbstractModel):
    _name = 'report.app_seleccion.report_application'


    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('app_seleccion.report_application')
        ids = self.env['hr.applicant'].search([])
        docargs = {
            #'doc_ids': docids,
            'doc_model': report.model,
            'docs': ids,
        }
        return report_obj.render('app_seleccion.report_application', docargs)

    # @api.model
    # def render_html(self, docids, data=None):
    #     report_obj = self.env['ir.actions.report']
    #     report = report_obj._get_report_from_name('app_seleccion.report_application')
    #     ids = self.env['hr.applicant'].search([])
    #     doc_args = {
    #         #'doc_ids': self.ids,
    #         'doc_model': report.model,
    #         'docs': ids,
    #     }
    #     return report_obj.render('app_seleccion.report_application',doc_args)

