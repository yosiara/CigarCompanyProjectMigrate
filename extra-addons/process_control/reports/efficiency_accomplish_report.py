# -*- coding: utf-8 -*-


from odoo import models, api


class EfficiencyAccomplishReport(models.AbstractModel):
    _name = 'report.turei_process_control.efficiency_accomplish_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('turei_process_control.efficiency_accomplish_report')

        productives_sections = self.env['turei_process_control.productive_section'].search([])
        records = []

        for productive_section in productives_sections:
            efficiency = productive_section.calculate_efficiency(data['date_start'], data['date_end'])
            if efficiency < data['percent']:
                records.append((productive_section, efficiency))

        docargs = {
            'doc_model': report.model,
            'docs': records,
            'data': data,
        }

        return report_obj.render('turei_process_control.efficiency_accomplish_report', docargs)
