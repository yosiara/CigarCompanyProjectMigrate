# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductiveLine(models.Model):
    _name = "process_control_primary.productive_line"
    _description = tools.ustr("Línea Productiva")
    _order = 'name'
    _rec_name = 'name'

    def _get_default_name(self):
        return 'Línea '

    name = fields.Char('Nombre', size=40, required=True, copy=False, default=_get_default_name)
    codigo = fields.Char('Codigo')
    machine_type_ids = fields.Many2many('process_control_primary.machine_type',
                                   relation="process_control_primary_produc_line_machine_type_asoc",
                                   column1="prod_line_id", copy=False,
                                   column2="machine_type_id", string='Máquinas')


    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la línea productiva debe ser único.'),
    ]

    def calculate_cdt(self, date_start=None, date_end=None):
        self.ensure_one()
        domain = [('productive_line', '=', self.id)]
        if date_start and date_end:
            domain.append(('date', '<=', date_end))
            domain.append(('date', '>=', date_start))
        else:
            raise ValidationError('El CDT debe calcularse en un rango de fechas.')

        control_models = self.env['process_control_primary.tecnolog_control_model'].search(domain)
        tpend, cdt, suma_plan_time = 0.0, 0.0, 0
        for tc in control_models:
            suma_plan_time += tc.plan_time
            for it in tc.interruptions:
                if it.interruption_type.cause == 'endogena':
                    tpend += it.time
        cdt = round(((suma_plan_time - (tpend / 60)) / suma_plan_time) * 100, 2)
        return cdt




