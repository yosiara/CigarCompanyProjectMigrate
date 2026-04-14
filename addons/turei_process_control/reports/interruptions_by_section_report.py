# -*- coding: utf-8 -*-


from odoo import models, api


class ReportInterruptionsBySection(models.AbstractModel):
    _name = 'report.turei_process_control.interruptions_by_section_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('turei_process_control.interruptions_by_section_report')

        records = {}
        domain = [('date', '>=', data['date_start']), ('date', '<=', data['date_end'])]

        if data['productive_section']:
            domain.append(('productive_section', '=', data['productive_section']))

        controles = self.env['turei_process_control.tecnolog_control_model'].search(domain)

        for control in controles:
            if data['interruption_type']:
                interrupciones = control.interruptions.filtered(
                    lambda i: i.interruption_type.id == data['interruption_type'])
            else:
                interrupciones = control.interruptions

            if len(interrupciones) > 0:
                seccion = control.productive_section.name
                if seccion not in records:
                    records[seccion] = {}

                for interrupcion in interrupciones:
                    tipo = interrupcion.interruption_type.name
                    if tipo not in records[seccion]:
                        records[seccion][tipo] = {'cantidad': 0, 'tiempo': 0}
                    records[seccion][tipo]['cantidad'] += 1
                    records[seccion][tipo]['tiempo'] += interrupcion.time

        docargs = {
            'doc_model': report.model,
            'docs': records,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
        }
        return report_obj.render('turei_process_control.interruptions_by_section_report', docargs)
