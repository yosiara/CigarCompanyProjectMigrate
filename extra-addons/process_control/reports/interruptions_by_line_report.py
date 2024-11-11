# -*- coding: utf-8 -*-


from odoo import models, api


class ReportInterruptionsByLine(models.AbstractModel):
    _name = 'report.process_control.interruptions_by_line_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('process_control.interruptions_by_line_report')

        records = {}
        domain = [('date', '>=', data['date_start']), ('date', '<=', data['date_end'])]
        if data['productive_line']:
            productive_line = self.env['process_control.productive_section_lines'].search(
                [('productive_line', '=', data['productive_line'])], limit=1)
            domain.append(('productive_section_id', '=', productive_line.productive_section_id.id))

        controles = self.env['process_control.tecnolog_control'].search(domain)

        for control in controles:
            if data['interruption_type']:
                interrupciones = control.interruption_ids.filtered(
                    lambda i: i.interruption_type.id == data['interruption_type'])
            else:
                interrupciones = control.interruption_ids

            if len(interrupciones) > 0:
                for interrupcion in interrupciones:
                    tipo = interrupcion.interruption_type.name
                    linea = None
                    if interrupcion.productive_line_id:
                        linea = interrupcion.productive_line_id.productive_line.name
                    if linea is not None:
                        if linea not in records:
                            records[linea] = {}
                        if tipo not in records[linea]:
                            records[linea][tipo] = {'cantidad': 0, 'tiempo': 0}
                        records[linea][tipo]['cantidad'] += 1
                        records[linea][tipo]['tiempo'] += interrupcion.time

        docargs = {
            'doc_model': report.model,
            'docs': records,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
        }
        return report_obj.render('process_control.interruptions_by_line_report', docargs)
