# -*- coding: utf-8 -*-
from odoo import models, api


class InterruptionsPdfReport(models.AbstractModel):
    _name = "report.process_control.interruptions_pdf_report"
    _description = "Interruptions pdf report"

    @api.model
    def _get_report_values(self, docids, data=None):
        res = {}
        
        domain = [('date', '>=', data['start_date']), ('date', '<=', data['end_date'])] # Domain for tecnolog_control
        if data['productive_section_id']:
            domain.append(('productive_section_id', '=', data['productive_section_id']))
        tecnolog_control = self.env['process_control.tecnolog_control'].search(domain)
        
        ids = []
        for tc in tecnolog_control:
            for i in tc.interruption_ids:
                ids.append(i.id)
        interruptions = self.env["process_control.interruption"].browse(ids)
        
        domain = [] # Domain for interruptions
        if data["interruption_type_id"]:
            domain.append('interruption_type_id', '=', data["interruption_type_id"])
        
        match data["filter"]:
            case "machine":
                if data["machine_id"]:
                    domain.append(('machine_id', '=', data["machine_id"]))
                    #return interruptions.filtered_domain(domain)
            case "productive_line":
                if data["productive_line_id"]:
                    domain.append(('productive_line_id', '=', data["productive_line_id"]))
                    interruptions = interruptions.filtered_domain(domain)
                    for i in interruptions:
                        type = i.interruption_type_id.name
                        line = None
                        if i.productive_line_id:
                            line = i.productive_line_id.name
                        if line is not None:
                            if line not in res:
                                res[line] = {}
                            if type not in res[line]:
                                res[line][type] = {'cantidad': 0, 'tiempo': 0}
                            res[line][type]['cantidad'] += 1
                            res[line][type]['tiempo'] += i.end_date - i.start_date
                        #res = interruptions.filtered_domain(domain)
            case "productive_section":
                interruptions = interruptions.filtered_domain(domain)
                if interruptions:
                    for tc in tecnolog_control:
                        section = tc.productive_section_id.name
                        if section not in res:
                            res[section] = {}
                        for i in interruptions:
                            type = i.interruption_type_id.name
                            if type not in res[section]:
                                res[section][type] = {'cantidad': 0, 'tiempo': 0}
                            res[section][type]['cantidad'] += 1
                            res[section][type]['tiempo'] += i.end_date - i.start_date
        
        return {
            #'doc_model': report.model,
            'docs': res,
            'start_date': data['start_date'],
            'end_date': data['end_date'],
        }
       # return report_obj.render('process_control.interruptions_by_section_report', docargs)
