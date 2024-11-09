# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdProdAndRegAmf(models.AbstractModel):
    _name = 'report.turei_process_control.prod_and_reg_amf_report'

    def get_prod_and_reg(self, date_start, date_end, turn=False):
        domain = [('date', '>=', date_start), ('date', '<=', date_end)]
        if turn:
            domain.append(('turn', '=', turn))
        control_mods = self.env['turei_process_control.tecnolog_control_model'].search(domain).mapped(
            'productive_section')
        return control_mods

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('turei_process_control.prod_and_reg_amf_report')
        productive_lines = self.env['turei_process_control.productive_section_lines'].search([])
        machine_type_ids = self.env['turei_process_control.machine_type'].search([('name', 'ilike', 'AMF')]).ids
        productive_lines_aux = []
        for pl in productive_lines:
            for machine in pl.productive_line.machine_ids:
                if machine.machine_type_id.id in machine_type_ids:
                    productive_lines_aux.append(pl)
                    break

        if data['turn']:
            turn_obj = self.env['resource.calendar'].search([('id', '=', data['turn'])])
        else:
            turn_obj = None

        docargs = {
            'doc_model': report.model,
            'docs': {},
            # 'docs': self.get_prod_and_reg(data['date_start'], data['date_end'], data['turn']),
            'turn': data['turn'],
            'turn_obj': turn_obj,
            'productive_lines_aux': productive_lines_aux,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
        }

        return report_obj.render('turei_process_control.prod_and_reg_amf_report', docargs)
