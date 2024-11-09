# -*- coding: utf-8 -*-


from odoo import models, api


class ReportInterruptionsByLine(models.AbstractModel):
    _name = 'report.turei_process_control.interruptions_by_machine_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('turei_process_control.interruptions_by_line_report')

        records = {}
        domain = [('date', '>=', data['date_start']), ('date', '<=', data['date_end'])]

        controles = self.env['turei_process_control.tecnolog_control_model'].search(domain)

        for control in controles:
            if data['interruption_type']:
                interrupciones = control.interruptions.filtered(
                    lambda i: i.interruption_type.id == data['interruption_type'])
            else:
                interrupciones = control.interruptions

            if len(interrupciones) > 0:
                for interrupcion in interrupciones:
                    tipo = interrupcion.interruption_type.name
                    machine = None
                    set_of_peaces_id = None
                    if interrupcion.machine_id:
                        if data['machine'] and interrupcion.machine_id.id == data['machine']:
                            machine = interrupcion.machine_id.name
                        elif not data['machine']:
                            machine = interrupcion.machine_id.name
                        else:
                            machine = None
                        if interrupcion.set_of_peaces_id and interrupcion.set_of_peaces_id is not None:
                            if not data['subset']:
                                set_of_peaces_id = interrupcion.set_of_peaces_id.name
                            elif interrupcion.set_of_peaces_id.id == data['subset']:
                                set_of_peaces_id = interrupcion.set_of_peaces_id.name
                            else:
                                continue

                    if machine is not None:
                        if machine not in records:
                            records[machine] = {}
                        if set_of_peaces_id is not None:
                            if set_of_peaces_id not in records[machine]:
                                records[machine].update({set_of_peaces_id: {}})
                        elif '' not in records[machine]:
                            records[machine].update({'': {}})
                            set_of_peaces_id = ''
                        else:
                            set_of_peaces_id = ''

                        if tipo not in records[machine][set_of_peaces_id]:
                            records[machine][set_of_peaces_id][tipo] = {'cantidad': 0, 'tiempo': 0}

                        records[machine][set_of_peaces_id][tipo]['cantidad'] += 1
                        records[machine][set_of_peaces_id][tipo]['tiempo'] += interrupcion.time

        docargs = {
            'doc_model': report.model,
            'docs': records,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
        }
        return report_obj.render('turei_process_control.interruptions_by_machine_report', docargs)
