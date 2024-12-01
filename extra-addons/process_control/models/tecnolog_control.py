# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class TecnologControl(models.Model):
    _name = 'process_control.tecnolog_control'
    _inherit = ["mail.activity.mixin", "mail.thread"]
    #_translate = False

    date = fields.Date(string="Fecha *", required=True, copy=True, default=fields.Date.today)
    # year_char = fields.Char(string=u"Año", required=False)
    # day_char = fields.Char(string=u"Día", required=False)
    turn_id = fields.Many2one(comodel_name="process_control.turn", string="Turno *", required=True, copy=True)

    turn_attendance_id = fields.Many2one('process_control.turn_attendance', string='Sesión *', copy=True, required=True)
    turn_attendance_domain = fields.Binary(compute="_compute_turn_attendance_domain", exportable=False)

    productive_section_id = fields.Many2one(comodel_name="process_control.productive_section", string="Módulo *", required=True)
    productive_capacity = fields.Integer('Capacidad Prod. *', required=True)
    plan_time = fields.Integer('Tmpo. Plan(Horas) *', required=True)

    # def _get_default_tec_model_type(self):
    #     if self.productive_section_id:
    #         self.tec_model_type = self.productive_section_id.tec_model_type

    # tec_model_type = fields.Selection(string="Documento/control", selection=[('mod', 'Módulo'), ('mod1', 'Módulo 1')], default=_get_default_tec_model_type)

    interruption_ids = fields.One2many(comodel_name="process_control.interruption", inverse_name="tecnolog_control_id", string="Interrupciones")

    #production_by_hours_ids = fields.One2many(comodel_name="process_control.production_by_hours", inverse_name="tecnolog_control_id", string="Produccion Horaria", required=False)

    # production_in_production_system = fields.Float(string="Prod. Sistema prod.", readonly=True,
    #                                                compute="get_production_in_production_system",
    #                                                help="Muestra producción registraba en el sistema de producción.")

    #production_in_proccess_control = fields.Float(string="Prod. calculada en el sistema.", readonly=True, store=True, compute='_compute_total_prod')

    # rechazo_amf_ids = fields.One2many(comodel_name="process_control.rechazo_amf",
    #                              inverse_name="tecnolog_control_id",
    #                              string="Rechazo de las AMF", required=False)

    #rechazo_mod1_ids = fields.One2many(comodel_name="process_control.rechazo_mod1", inverse_name="tecnolog_control_id", string="Rechazo 'NANO', 'SBO', 'SRC'", required=False)

    name = fields.Char(string="Nombre", default="Documento de control")

    # _sql_constraints = [('turn_calendar_id_in_date_uniq', 'unique(turn_calendar_id,date,productive_section_id,attendance_id)',
    #                      "Ya existe un modelo registrado para el turno (Sesión) en la fecha seleccionada."),
    #                     ('attendance_in_productive_uniq', 'unique(date,productive_section_id,attendance_id)',
    #                      "Ya existe un modelo registrado para esa Sesión en la fecha seleccionada.")]

    # @api.model
    # def default_get(self, fields):
    #     res = super(TecnologControl, self).default_get(fields)
    #     rec_last = self.search([], order='id desc', limit=1)
    #     if rec_last:
    #         res["date"] = rec_last.date
    #         res["turn_calendar_id"] = rec_last.turn_calendar_id.id
    #         res["attendance_id"] = rec_last.attendance_id.id
    #     return res

    # @api.depends('date')
    # def _compute_year_char(self):
    #     for c_model in self:
    #         date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
    #         c_model.year_char = str(date.year)

    # @api.depends('date')
    # def _compute_day_char(self):
    #     for c_model in self:
    #         date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
    #         if int(date.day) < 10:
    #             c_model.day_char = "0"+str(date.day)
    #         else:
    #             c_model.day_char = str(date.day)

    # @api.constrains('plan_time')
    # def check_plan_time(self):
    #     if self.plan_time:
    #         try:
    #             if self.plan_time < 1:
    #                 raise ValidationError('Tiempo planificado debe ser un número mayor que 0.')
    #         except Exception:
    #             raise ValidationError('Tiempo planificado debe ser un número mayor que 0.')

    # @api.constrains('production_by_hours_ids')
    # def check_production_by_hours_ids(self):
    #     #if self.production_in_production_system == self.production_in_proccess_control == 0:
    #         #pass
    #         #raise ValidationError('Producción registrada no puede ser 0')
    #     if self.production_in_production_system != self.production_in_proccess_control:
    #         self.env.user.notify_info(
    #             'Producción registrada no coincide con la registrada en el sistema de producción.')
    #         # raise ValidationError('Producción registrada no coincide con la registrada en el sistema de producción.')

    # @api.depends('turn_calendar_id', 'productive_section_id', 'date')
    # def get_production_in_production_system(self):
    #     if self.turn_calendar_id and self.productive_section_id and self.date:
    #         connexion = self.env['db_external_connector'].search([('application', '=', 'sgp')], limit=1)
    #         connexion.ensure_one()
    #         res = []
    #         self.production_in_production_system = 0
    #         if connexion:
    #             try:
    #                 cursor = connexion.connect().cursor()
    #                 query = """SELECT SUM(cantidad_producida) FROM pt_produccion_terminada
    # WHERE id_modulo = %d AND id_turno = %d and fecha = '%s'""" % (
    #                     int(self.productive_section_id.production_id), self.turn_calendar_id.sgp_turn_id, self.date)
    #                 cursor.execute(query)
    #                 for row in cursor:
    #                     self.production_in_production_system = row[0]
    #             except Exception:
    #                 pass

    # @api.model_create_multi
    # def create(self, vals_list):
    #     print(self)
    #     print(vals_list)
    #     return super().create(vals_list)

    @api.depends("turn_id")
    def _compute_turn_attendance_domain(self):
        if self.turn_id:
            self.turn_attendance_domain = [('turn_id', '=', self.turn_id.id)]
        else:
            self.turn_attendance_domain = [('turn_id', '=', False)]

    @api.onchange("productive_section_id")
    def _onchange_productive_section_id(self):
        if self.productive_section_id:
            self.interruption_ids.unlink()

    # def _create_domain(self, fname, value):
    #     if not fname == 'account_prefix':
    #         return super()._create_domain(fname, value)

    # @api.onchange('turn_calendar_id')
    # def _onchange_turn_calendar_id(self):
    #     if self.turn_calendar_id:
    #         #attendace_ids = self.env['resource.calendar.attendance'].search([('calendar_id', '=', self.turn_calendar_id.id)])
    #         #print(len(attendace_ids))
    #         # self.attendance_id = False
    #         #domains = {'domain': {'attendance_id': [('calendar_id', '=', self.turn_calendar_id.id)]}}
            
    #         #print(domains)
    #         return super(TecnologControl, self.attendance_id).filtered_domain(domain=[('calendar_id', '=', self.turn_calendar_id.id)])
    #     return {'domain': {'attendance_id': [('calendar_id', 'in', [])]}}

    # @api.model_create_multi
    # @api.onchange('attendance_id')
    # def _onchange_attendance_id(self):
    #     if self.attendance_id.id:
    #         list_hours = []
    #         self.production_by_hours_ids = False
    #         date_start = datetime.strptime(str(int(self.attendance_id.hour_from)), '%H')
    #         date_end = datetime.strptime(str(int(self.attendance_id.hour_to)), '%H')
    #         timedelta_diff = date_end - date_start
    #         iter_count = int(timedelta_diff.seconds / 3600)
    #         hours_counter = 1
    #         sufix = {0: 'ra', 1: 'da', 2: 'ra', 3: 'ta', 4: 'ta', 5: 'ta', 6: 'ma', 7: 'va', 8: 'na', 9: 'ma'}
    #         for i in range(0, iter_count, 1):
    #             aux_sufix = ''
    #             if i in sufix:
    #                 aux_sufix = sufix[i]
    #             list_hours.append(
    #                 [0, 0,
    #                  {'hour_production': str(1 + i) + aux_sufix + ' hora ' + date_start.strftime('%H:%M') + ' a ' +
    #                                      (date_start + timedelta(hours=hours_counter)).strftime('%H:%M')}])
    #             hours_counter += 1
    #             self.production_by_hours_ids = list_hours
    #         self._compute_plan_time()

    # @api.depends('attendance_id')
    # def _compute_plan_time(self):
    #     for att in self:
    #         date_start = datetime.strptime(str(int(att.attendance_id.hour_from)), '%H')
    #         date_end = datetime.strptime(str(int(att.attendance_id.hour_to)), '%H')
    #         timedelta_diff = date_end - date_start
    #         att.plan_time = int(timedelta_diff.seconds / 3600)

    # @api.model_create_multi
    # @api.onchange('productive_section_id')
    # def _onchange_productive_section_id(self):
    #     if self.productive_section_id.id:
    #         self.production_by_hours_ids = False
    #         self.interruption_ids = False
    #         self.rechazo_amf_ids = False
    #         self.rechazo_mod1_ids = False
    #         self.tec_model_type = self.productive_section_id.tec_model_type
    #         self.productive_capacity = self.productive_section_id.get_efficiency_plan().productive_capacity
    #         self._onchange_attendance_id()

    #         list_lines = []
    #         for line in self.productive_section_id.productive_line_ids:
    #             if self.productive_section_id.tec_model_type == 'mod':
    #                 machine_type_id = self.env['process_control.machine_type'].search([('name', '=', 'AMF')])
    #                 machine_ids = line.productive_line.machine_ids.search([('machine_type_id', '=', machine_type_id.id),
    #                                                                    ('id', 'in',
    #                                                                     line.productive_line.machine_ids.ids)], limit=1)
    #                 list_lines.append([0, 0, {
    #                     'productive_line_id': line.id,
    #                     'machine_id': machine_ids.id
    #                 }])
    #                 self.rechazo_amf_ids = list_lines
    #             # else:
    #             #     list_lines.append([0, 0, {
    #             #         'productive_line_id': line.id,
    #             #     }])
    #             #     self.rechazo_mod1_ids = list_lines

    
    # @api.depends('production_by_hours_ids.production_count')
    # def _compute_total_prod(self):
    #     for mod in self:
    #         if mod.production_by_hours_ids:
    #             total = 0
    #             for prod in mod.production_by_hours_ids:
    #                 total += prod.production_count
    #             mod.production_in_proccess_control = total

    # @api.model_create_multi
    # def create(self, vals_list):
        # if 'production_by_hours_ids' in vals:
        #     no_extra_hr = 1
        #     for ph in vals['production_by_hours_ids']:
        #         if ph[2]['hour_production'] == 'Hora extra ':
        #             ph[2]['hour_production'] += str(no_extra_hr)
        #             no_extra_hr += 1
        # return super(TecnologControl, self).create(vals)

    # @api.model
    # def write(self, vals):
        # if 'production_by_hours_ids' in vals:
        #     no_extra_hr = 1
        #     for ph in vals['production_by_hours_ids']:
        #         if ph[2] and 'hour_production' in ph[2]:
        #             if ph[2]['hour_production'] == 'Hora extra ':
        #                 ph[2]['hour_production'] += str(no_extra_hr)
        #                 no_extra_hr += 1
        # return super(TecnologControl, self).write(vals)

