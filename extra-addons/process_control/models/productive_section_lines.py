# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class ProductiveSectionLines(models.Model):
    _name = 'process_control.productive_section_lines'
    _rec_name = 'productive_line'


    productive_section_id = fields.Many2one(comodel_name="process_control.productive_section",
                                            string="Módulo", required=False)

    productive_line = fields.Many2one(comodel_name="process_control.productive_line", string="Línea Productiva",
                                      required=False)
    name = fields.Char(string="Nombre", required=False, related='productive_line.name')
    productive_section_name = fields.Char(string="Nombre", required=True, compute='get_section_name', store=True)

    @api.model_create_multi
    @api.depends('productive_section_id.name')
    def get_section_name(self):
        for ps in self:
            ps.productive_section_name = ps.productive_section_id.name

    def get_product_amf_productive_line(self, start_date, end_date, turn=False):
        self.ensure_one()
        domain = [('date', '>=', start_date), ('date', '<=', end_date),
                  ('productive_section_id', '=', self.productive_section_id.id)]
        if turn:
            domain.append(('turn_calendar_id', '=', turn))
        control_mods = self.env['process_control.tecnolog_control'].search(domain)
        res = {}
        for cm in control_mods:
            for line in cm.rechazo_amf_ids:
                if line.productive_line_id.productive_line.id not in res:
                    res.update({line.productive_line_id.productive_line.id: 0.00})
                res[line.productive_line_id.productive_line.id] += line.produccion_en_cajones
        return res

    def get_reg_amf_by_productive_line(self, start_date, end_date, turn=False):
        self.ensure_one()
        domain = [('date', '>=', start_date), ('date', '<=', end_date),
                  ('productive_section_id', '=', self.productive_section_id.id)]
        if turn:
            domain.append(('turn_calendar_id', '=', turn))
        control_mods = self.env['process_control.tecnolog_control'].search(domain)
        res = {}
        for cm in control_mods:
            for line in cm.rechazo_amf_ids:
                if line.productive_line_id.productive_line.id not in res:
                    res.update({line.productive_line_id.productive_line.id: 0.00})
                res[line.productive_line_id.productive_line.id] += round(line.rechazo_en_cajetijas / 500.00, 3)
        return res

    def get_reg_ind(self, start_date, end_date, turn=False, line_id=False):
        # calcular indice de rechazo de la linea
        self.ensure_one()
        prod = self.get_product_amf_productive_line(start_date, end_date, turn)
        reg = self.get_reg_amf_by_productive_line(start_date, end_date, turn)
        if line_id in prod:
            prod = prod[line_id]
        else:
            prod = 1
        if line_id in reg:
            reg = reg[line_id]
        else:
            reg = 0

        if prod+reg > 0:
            return round((reg / (prod+reg)) * 100.00, 3)
        return 0
