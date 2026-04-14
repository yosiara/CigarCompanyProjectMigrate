# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductiveLine(models.Model):
    _name = "turei_process_control.productive_line"
    _description = tools.ustr("Línea Productiva")
    _order = 'name'

    def _get_default_name(self):
        return 'Línea #'

    name = fields.Char('Nombre', size=40, required=True, copy=False, default=_get_default_name)
    machine_ids = fields.Many2many('turei_process_control.machine',
                                   relation="turei_process_control_produc_line_machine_asoc",
                                   column1="prod_line_id", copy=False,
                                   column2="machine_id", string='Máquinas')
    is_in_productive_section = fields.Boolean('Añadido a sección productiva', compute='is_in_productive_section_check')

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la línea productiva debe ser único.'),
    ]

    @api.multi
    def name_get(self):
        if 'productive_section' in self._context:
            resp_list = []
            for line in self:
                if not line.is_in_productive_section:
                    name = tools.ustr(line.name)
                    resp_list.append((line.id, name))
            return resp_list
        return super(ProductiveLine, self).name_get()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if 'productive_section' in self._context:
            valid_ids = []
            no_valid_ids = []
            domain = [('id', 'not in', no_valid_ids)]
            prod_line = self.search(domain + args, limit=limit)
            while len(prod_line) > 0 and limit > 0:
                for line in prod_line:
                    if not line.is_in_productive_section:
                        valid_ids.append(line.id)
                        no_valid_ids.append(line.id)
                        limit -= 1
                    else:
                        no_valid_ids.append(line.id)
                prod_line = self.search(domain + args, limit=limit)
            return self.browse(valid_ids).name_get()
        return super(ProductiveLine, self).name_search(name, args, operator, limit)

    @api.multi
    def is_in_productive_section_check(self):
        for line in self:
            inserted = self.env['turei_process_control.productive_section_lines'].search(
                [('productive_line.id', '=', line.id)])
            line.is_in_productive_section = False if len(inserted) == 0 else True
