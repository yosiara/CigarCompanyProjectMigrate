# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError


class ProductiveSection(models.Model):
    _name = "turei_process_control.productive_section"
    _rec_name = 'name'
    _description = tools.ustr("Modulo")
    _order = 'name'

    def _get_default_name(self):
        return 'Modulo '

    def _get_productions_code(self):
        connexion = self.env['db_production_connector.template'].search([], limit=1)
        #connexion.ensure_one()
        res = []
        if connexion:
            try:
                conn = connexion.connect()
                cursor = conn.cursor()
                cursor.execute("""SELECT "id", descripcion FROM cd_modulo WHERE id > 0 ORDER BY id""")
                for row in cursor:
                    res.append((str(row[0]), str(row[1])))
            except Exception:
                pass
        return res

    name = fields.Char('Nombre', size=40, required=True, copy=False, default=_get_default_name)
    production_id = fields.Selection(string="Id producción", selection=_get_productions_code, required=False,
                                     help='Id en el sistema de producción.')
    tec_model_type = fields.Selection(string="Documento/control",
                                      selection=[('mod', 'Módulo'), ('mod1', 'Módulo 1'), ], required=False,
                                      default='mod')
    productive_line_ids = fields.One2many('turei_process_control.productive_section_lines',
                                          inverse_name='productive_section_id',
                                          string='Líneas Productivas')

    productive_section_plan = fields.Many2one('turei_process_control.productive_section_plan', string='Norma plan')
    active = fields.Boolean(string="Activa", default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
         'El nombre de la Modulo debe ser único.'),
    ]

    @api.constrains('productive_line_ids')
    def check_productive_line_just_in_one_section(self):
        for productive_section_lines in self.productive_line_ids:
            lines_in_system = self.env['turei_process_control.productive_section_lines'].search(
                [('productive_line.id', '=', productive_section_lines.productive_line.id)], limit=2)
            if len(lines_in_system) > 1:
                raise ValidationError(
                    u'La línea productiva: "' + tools.ustr(
                        productive_section_lines.productive_line.name)
                    + u'" ya ha sido añadida en la Modulo: "' +
                    tools.ustr(lines_in_system[0].productive_section_id.name) + '"')

    def calculate_cdt(self, date_start=None, date_end=None, turn=None):
        self.ensure_one()
        domain = [('productive_section', '=', self.id)]
        if date_start and date_end:
            domain.append(('date', '<=', date_end))
            domain.append(('date', '>=', date_start))
        else:
            raise ValidationError('El CDT debe calcularse en un rango de fechas.')

        if turn:
            domain.append(('turn', '=', turn))

        count_lines = len(self.productive_line_ids)
        control_models = self.env['turei_process_control.tecnolog_control_model'].search(domain)

        cdt, sum_plan_time, sum_time_interruption, time_n_j = 0.00, 0.00, 0.00, 0.00

        for control_model in control_models:
            sum_plan_time += control_model.plan_time * 60
            for interruption in control_model.interruptions:
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
        domain = [('productive_section', '=', self.id)]
        if date_start and date_end:
            domain.append(('date', '<=', date_end))
            domain.append(('date', '>=', date_start))
        else:
            raise ValidationError('La eficiencia productiva debe calcularse en un rango de fechas.')

        if turn:
            domain.append(('turn', '=', turn))

        control_models = self.env['turei_process_control.tecnolog_control_model'].search(domain)

        production_done, efficiency, time_planned, productive_capacity, productividad_real = (0.00, 0.00, 0.00, 0.00, 0.00)

        for control_model in control_models:
            production_done += control_model.production_in_proccess_control
            # productive_capacity += control_model.productive_capacity
            productive_capacity += self.get_efficiency_plan().productive_capacity
            productividad_real += control_model.plan_time * 60 * self.get_efficiency_plan().productive_capacity  # control_model.productive_capacity
        if productive_capacity and production_done > 0.00:
            efficiency = round(((production_done * 10000.00) / productividad_real) * 100.00, 2)

        return efficiency

    @api.multi
    def get_efficiency_plan(self):
        self.ensure_one()
        return self.env['turei_process_control.productive_section_plan'].search([('productive_section_ids', 'in', self.id), ('active', '=', True)])

    def get_ind_rechazo(self, date_start, date_end, turn=False):
        suma_ind = 0.00
        for line in self.productive_line_ids:
            suma_ind += line.get_reg_ind(date_start, date_end, turn, line.productive_line.id)
        # return round(suma_ind/len(self.productive_line_ids), 3)
        return round(suma_ind / self.get_efficiency_plan().quantity_line, 3)


class ProductiveSectionLines(models.Model):
    _name = 'turei_process_control.productive_section_lines'
    _rec_name = 'productive_line'


    productive_section_id = fields.Many2one(comodel_name="turei_process_control.productive_section",
                                            string="Modulo", required=False, )

    productive_line = fields.Many2one(comodel_name="turei_process_control.productive_line", string="Línea Produtiva",
                                      required=False)
    name = fields.Char(string="nombre", required=False, related='productive_line.name')
    productive_section_name = fields.Char(string="nombre", required=True, compute='get_section_name', store=True)

    @api.multi
    @api.depends('productive_section_id.name')
    def get_section_name(self):
        for ps in self:
            ps.productive_section_name = ps.productive_section_id.name

    def get_product_amf_productive_line(self, date_start, date_end, turn=False):
        self.ensure_one()
        domain = [('date', '>=', date_start), ('date', '<=', date_end),
                  ('productive_section', '=', self.productive_section_id.id)]
        if turn:
            domain.append(('turn', '=', turn))
        control_mods = self.env['turei_process_control.tecnolog_control_model'].search(domain)
        res = {}
        for cm in control_mods:
            for line in cm.rechazo_amf:
                if line.productive_line_id.productive_line.id not in res:
                    res.update({line.productive_line_id.productive_line.id: 0.00})
                res[line.productive_line_id.productive_line.id] += line.produccion_en_cajones
        return res

    def get_reg_amf_by_productive_line(self, date_start, date_end, turn=False):
        self.ensure_one()
        domain = [('date', '>=', date_start), ('date', '<=', date_end),
                  ('productive_section', '=', self.productive_section_id.id)]
        if turn:
            domain.append(('turn', '=', turn))
        control_mods = self.env['turei_process_control.tecnolog_control_model'].search(domain)
        res = {}
        for cm in control_mods:
            for line in cm.rechazo_amf:
                if line.productive_line_id.productive_line.id not in res:
                    res.update({line.productive_line_id.productive_line.id: 0.00})
                res[line.productive_line_id.productive_line.id] += round(line.rechazo_en_cajetijas / 500.00, 3)
        return res

    def get_reg_ind(self, date_start, date_end, turn=False, line_id=False):
        # calcular indice de rechazo de la linea
        self.ensure_one()
        prod = self.get_product_amf_productive_line(date_start, date_end, turn)
        reg = self.get_reg_amf_by_productive_line(date_start, date_end, turn)
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
