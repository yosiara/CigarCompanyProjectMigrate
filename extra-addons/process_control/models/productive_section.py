# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductiveSection(models.Model):
    _name = "process_control.productive_section"
    _rec_name = 'name'
    _description = "Módulo"
    _order = 'name'

    def _get_default_name(self):
        return 'Módulo # '

    # def _get_productions_code(self):
    #     connexion = self.env['process_control.db_production_connector'].search([], limit=1)
    #     #connexion.ensure_one()
    #     res = []
    #     if connexion:
    #         try:
    #             conn = connexion.connect()
    #             cursor = conn.cursor()
    #             cursor.execute("""SELECT "id", descripcion FROM cd_modulo WHERE id > 0 ORDER BY id""")
    #             for row in cursor:
    #                 res.append((str(row[0]), str(row[1])))
    #         except Exception:
    #             pass
    #     return res

    name = fields.Char('Nombre *', size=40, required=True, copy=False, default=_get_default_name)
    # production_id = fields.Selection(string="Id producción", selection=_get_productions_code, required=False,
    #                                  help='Id en el sistema de producción.')
    # tec_model_type = fields.Selection(string="Documento/control",
    #                                   selection=[('mod', 'Módulo'), ('mod1', 'Módulo 1'), ], required=False,
    #                                   default='mod')
    # productive_line_ids = fields.One2many('process_control.productive_line',
    #                                       inverse_name='productive_section_id',
    #                                       string='Líneas Productivas')

    productive_section_plan_id = fields.Many2one('process_control.productive_section_plan', string='Plan *', required=True)
    active = fields.Boolean(string="Activa", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'El nombre del Módulo debe ser único.'),
    ]

    # @api.constrains('productive_line_ids')
    # def check_productive_line_just_in_one_section(self):
    #     for productive_section_lines in self.productive_line_ids:
    #         lines_in_system = self.env['process_control.productive_section_lines'].search(
    #             [('productive_line.id', '=', productive_section_lines.productive_line.id)], limit=2)
    #         if len(lines_in_system) > 1:
    #             raise ValidationError(
    #                 u'La línea productiva: "' + tools.ustr(
    #                     productive_section_lines.productive_line.name)
    #                 + u'" ya ha sido añadida en la Modulo: "' +
    #                 tools.ustr(lines_in_system[0].productive_section_id.name) + '"')

    def calculate_cdt(self, date_start=None, date_end=None, turn=None):
        self.ensure_one()
        domain = [('productive_section_id', '=', self.id)]
        if date_start and date_end:
            domain.append(('date', '<=', date_end))
            domain.append(('date', '>=', date_start))
        else:
            raise ValidationError('El CDT debe calcularse en un rango de fechas.')

        if turn:
            domain.append(('turn_calendar_id', '=', turn))

        count_lines = len(self.productive_line_ids)
        control_models = self.env['process_control.tecnolog_control'].search(domain)

        cdt, sum_plan_time, sum_time_interruption, time_n_j = 0.00, 0.00, 0.00, 0.00

        for control_model in control_models:
            sum_plan_time += control_model.plan_time * 60
            for interruption in control_model.interruption_ids:
                if not interruption.productive_line_id:
                    sum_time_interruption += interruption.time * count_lines
                else:
                    sum_time_interruption += interruption.time

        if sum_plan_time and count_lines > 0.00:
            time_n_j = sum_plan_time - (sum_time_interruption / count_lines)
            if time_n_j > 0:
                cdt = round(((sum_plan_time - (sum_time_interruption / count_lines)) / sum_plan_time) * 100, 2)
            else:
                cdt = round(((sum_plan_time - ((sum_time_interruption / count_lines) + time_n_j)) / sum_plan_time) * 100, 2)

        return cdt

    def calculate_efficiency(self, date_start=None, date_end=None, turn=None):
        self.ensure_one()
        domain = [('productive_section_id', '=', self.id)]
        if date_start and date_end:
            domain.append(('date', '<=', date_end))
            domain.append(('date', '>=', date_start))
        else:
            raise ValidationError('La eficiencia productiva debe calcularse en un rango de fechas.')

        if turn:
            domain.append(('turn_calendar_id', '=', turn))

        control_models = self.env['process_control.tecnolog_control'].search(domain)

        production_done, efficiency, time_planned, productive_capacity, productividad_real = (0.00, 0.00, 0.00, 0.00, 0.00)

        for control_model in control_models:
            production_done += control_model.production_in_proccess_control
            # productive_capacity += control_model.productive_capacity
            productive_capacity += self.get_efficiency_plan().productive_capacity
            productividad_real += control_model.plan_time * 60 * self.get_efficiency_plan().productive_capacity  # control_model.productive_capacity
        if productive_capacity and production_done > 0.00:
            efficiency = round(((production_done * 10000.00) / productividad_real) * 100.00, 2)

        return efficiency

    #@api.model_create_multi
    def get_efficiency_plan(self):
        self.ensure_one()
        return self.env['process_control.productive_section_plan'].search([('productive_section_ids', 'in', self.id), ('active', '=', True)])

    def get_ind_rechazo(self, date_start, date_end, turn=False):
        suma_ind = 0.00
        for line in self.productive_line_ids:
            suma_ind += line.get_reg_ind(date_start, date_end, turn, line.productive_line.id)
        # return round(suma_ind/len(self.productive_line_ids), 3)
        return round(suma_ind / self.get_efficiency_plan().quantity_line, 3)
