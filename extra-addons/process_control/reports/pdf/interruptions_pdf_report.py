# -*- coding: utf-8 -*-
from odoo import models, api
import logging
_logger = logging.getLogger(__name__)

class InterruptionsPdfReport(models.AbstractModel):
    _name = "report.process_control.interruptions_pdf_report"
    _description = "Interruptions pdf report"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = {}
        total = {
            'Total': {
                'cantidad': 0, 'tiempo': 0.00
            },
        }
        
        # Get tecnolog_control data
        domain = [('date', '>=', data['start_date']), ('date', '<=', data['end_date'])] # Domain for tecnolog_control
        if data['productive_section_ids']:
            domain.append(('productive_section_id', 'in', data['productive_section_ids']))
        tecnolog_control = self.env['process_control.tecnolog_control'].search(domain)
        
        # Get interruptions data in tecnolog_control
        ids = []
        for tc in tecnolog_control:
            for i in tc.interruption_ids:
                ids.append(i.id)
        interruptions = self.env["process_control.interruption"].browse(ids)

        domain = [] # Domain for interruptions
        if data["interruption_type_ids"]:
            domain.append(('interruption_type_id', 'in', data["interruption_type_ids"]))
        if data["machine_ids"]:
            domain.append(('machine_id', 'in', data["machine_ids"]))
        if data["set_of_peaces_ids"]:
            domain.append(('set_of_peaces_id', 'in', data["set_of_peaces_ids"]))
        elif data["productive_line_ids"]:
            domain.append(('productive_line_id', 'in', data["productive_line_ids"]))
        interruptions = interruptions.filtered_domain(domain)
        
        if not interruptions: # Empty Data
            _logger.warning('There is no data to display.')
            return
        
        # Processing data...
        match data["filt"]:
            case "machine":
                for i in interruptions:
                    if i.machine_id:
                        machine = i.machine_id.name
                        type = i.interruption_type_id.name
                        set_of_peaces = i.set_of_peaces_id.name if i.set_of_peaces_id else '-'
                        if machine not in res:
                            res[machine] = {}
                            total[machine] = {'cantidad': 0, 'tiempo': 0.00, 'rowspan': 0}
                        if set_of_peaces not in res[machine]:
                            res[machine][set_of_peaces] = {}
                            total[machine]['rowspan'] += 1
                        if type not in res[machine][set_of_peaces]:
                            res[machine][set_of_peaces][type] = {'cantidad': 0, 'tiempo': 0.00}
                            total[machine]['rowspan'] += 1
                        res[machine][set_of_peaces][type]['cantidad'] += 1
                        total[machine]['cantidad'] += 1
                        total['Total']['cantidad'] += 1
                        time = i.end_date - i.start_date
                        res[machine][set_of_peaces][type]['tiempo'] += time
                        total[machine]['tiempo'] += time
                        total['Total']['tiempo'] += time
                # for _, v in res.items():
                #     if '-' in v:
                #         val = v['-']
                #         del v['-']
                #         v['-'] = val              
            case "productive_line":
                for i in interruptions:
                    if i.productive_line_id:
                        line = i.productive_line_id.name
                        type = i.interruption_type_id.name
                        if line not in res:
                            res[line] = {}
                            total[line] = {'cantidad': 0, 'tiempo': 0.00}
                        if type not in res[line]:
                            res[line][type] = {'cantidad': 0, 'tiempo': 0.00}
                        res[line][type]['cantidad'] += 1
                        total[line]['cantidad'] += 1
                        total['Total']['cantidad'] += 1
                        time = i.end_date - i.start_date
                        res[line][type]['tiempo'] += time
                        total[line]['tiempo'] += time
                        total['Total']['tiempo'] += time
            case "productive_section":
                for tc in tecnolog_control:
                    for i in interruptions.filtered(lambda i: i.tecnolog_control_id.id == tc.id):
                        section = tc.productive_section_id.name
                        if section not in res:
                            res[section] = {}
                            total[section] = {'cantidad': 0, 'tiempo': 0.00}
                        type = i.interruption_type_id.name
                        if type not in res[section]:
                            res[section][type] = {'cantidad': 0, 'tiempo': 0.00}
                        res[section][type]['cantidad'] += 1
                        total[section]['cantidad'] += 1
                        total['Total']['cantidad'] += 1
                        time = i.end_date - i.start_date
                        res[section][type]['tiempo'] += time
                        total[section]['tiempo'] += time
                        total['Total']['tiempo'] += time

        return {
            #'doc_model': report.model,
            'res': res,
            'total': total,
            'filt': data["filt"],
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
       # return report_obj.render('process_control.interruptions_by_section_report', docargs)
