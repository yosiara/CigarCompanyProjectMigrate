# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class tecnolog_control_model(models.Model):
    _name = 'process_control_tobacco.tecnolog_control_model'

    date = fields.Date(string="Fecha", required=True, copy=True)
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)
    day_char = fields.Char(string=u"Día", required=False, compute="_compute_day_char", store=True)
    turn = fields.Many2one(comodel_name="process_control_tobacco.turno", string="Turno", domain=[('turn_process_control', '=', True)], required=True, copy=True)

    attendance_id = fields.Many2one('resource.calendar.attendance', string='Sesión', copy=True, required=True, )

    # productive_line = fields.Many2one(comodel_name="process_control_tobacco.productive_line",
    #                                      string="Línea productiva",
    #                                      required=True, ondelete='cascade')
    productive_capacity = fields.Integer('Capacidad Productiva', required=True, default=400)
    plan_time = fields.Integer('Tmpo. Plan(Horas)', required=True)


    interruptions = fields.One2many(comodel_name="process_control_tobacco.interruption", inverse_name="tec_control_model",
                                    string="Interrupciones", required=False, ondelete='cascade')

    reconstituted_produced = fields.Float(string="Reconstituido Producido (kg)", readonly=True,compute="get_reconstituted_produced", help="Muestra producción registraba en el sistema de producción.")

    execution_time_l100 = fields.Float('Tiempo Ejecución de la línea 100(Horas)', required=True)
    quantity_vena_polvo = fields.Float('Cantidad de polvo y vena procesada (Kg)', required=True)
    execution_time_l300 = fields.Float('Tiempo Ejecución de la línea 300(Horas)', required=True)

    name = fields.Char(string="Nombre", required=False, compute='_calc_name')

    production_by_hours_ids = fields.One2many(comodel_name="process_control_tobacco.production_by_hours",
                                              inverse_name="tecnolog_control_id",
                                              string="Producción Horaria", required=False)

    production_in_proccess_control = fields.Float(string="Prod calculada en el sistema.", readonly=True, store=True,
                                                  compute='_compute_total_prod')

    _sql_constraints = [('turn_in_date_uniq', 'unique(turn,date,attendance_id)',
                         "Ya existe un modelo registrado para el turno en la fecha seleccionada.")
                        ]

    @api.model
    def default_get(self, fields):
        res = super(tecnolog_control_model, self).default_get(fields)
        return res

    @api.multi
    @api.depends('date')
    def _compute_year_char(self):
        for c_model in self:
            date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
            c_model.year_char = str(date.year)

    @api.multi
    @api.depends('date')
    def _compute_day_char(self):
        for c_model in self:
            date = fields.datetime.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
            if int(date.day) < 10:
                c_model.day_char = "0"+str(date.day)
            else:
                c_model.day_char = str(date.day)

    @api.constrains('plan_time')
    def check_plan_time(self):
        if self.plan_time:
            try:
                if self.plan_time < 1:
                    raise ValidationError('Tiempo planificado debe ser un número mayor que 0.')
            except Exception:
                raise ValidationError('Tiempo planificado debe ser un número mayor que 0.')

    @api.onchange('turn')
    def get_attendance_ids(self):
        if self.turn:
            attendace_ids = self.env['resource.calendar.attendance'].search([('calendar_id.id', '=', self.turn.turn.id)])
            # self.attendance_id = False
            return {'domain': {'attendance_id': [('id', 'in', attendace_ids.ids)]}}
        return {'domain': {'attendance_id': [('calendar_id', 'in', [])]}}

    @api.onchange('attendance_id')
    def _onchange_attendance_id(self):
        if self.attendance_id:
            for att in self:
                date_start = datetime.strptime(str(int(att.attendance_id.hour_from)), '%H')
                date_end = datetime.strptime(str(int(att.attendance_id.hour_to)), '%H')
                timedelta_diff = date_end - date_start
                att.plan_time = int(timedelta_diff.seconds / 3600)

    @api.multi
    def _calc_name(self):
        for doc in self:
            doc.name = "Documento de control"

    @api.depends('turn', 'date')
    def get_reconstituted_produced(self):
        for c_model in self:
            if c_model.turn and c_model.date:
                connexion = self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)
                connexion.ensure_one()
                res = []
                c_model.reconstituted_produced = 0
                if connexion:
                    try:
                        cursor = connexion.connect().cursor()
                        query = """SELECT cantidad FROM ptrc_datos_productivos
        WHERE id_referencia = 16 AND id_turno = %d and fecha = '%s'""" % (c_model.turn.turn.sgp_turn_id, c_model.date)
                        cursor.execute(query)
                        for row in cursor:
                            c_model.reconstituted_produced = row[0]
                    except Exception, e:
                        pass

    @api.onchange('turn', 'date')
    def _onchange_reconstituted_produced(self):
        if self.turn and self.date:
            connexion = self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)
            connexion.ensure_one()
            res = []
            self.reconstituted_produced = 0
            if connexion:
                try:
                    cursor = connexion.connect().cursor()
                    query = """SELECT cantidad FROM ptrc_datos_productivos
    WHERE id_referencia = 16 AND id_turno = %d and fecha = '%s'""" % (self.turn.turn.sgp_turn_id, self.date)
                    cursor.execute(query)
                    for row in cursor:
                        self.reconstituted_produced = row[0]
                except Exception, e:
                    pass

    @api.multi
    @api.depends('production_by_hours_ids.production_count')
    def _compute_total_prod(self):
        for mod in self:
            if mod.production_by_hours_ids:
                total = 0
                for prod in mod.production_by_hours_ids:
                    total += prod.production_count
                mod.production_in_proccess_control = total

    @api.onchange('attendance_id')
    def _onchange_attendance_id(self):
        if self.attendance_id:
            list_hours = []
            self.production_by_hours_ids = False
            date_start = datetime.strptime(str(int(self.attendance_id.hour_from)), '%H')
            date_end = datetime.strptime(str(int(self.attendance_id.hour_to)), '%H')
            timedelta_diff = date_end - date_start
            iter_count = int(timedelta_diff.seconds / 3600)
            hours_counter = 1
            sufix = {0: 'ra', 1: 'da', 2: 'ra', 3: 'ta', 4: 'ta', 5: 'ta', 6: 'ma', 7: 'va', 8: 'na', 9: 'ma'}
            for i in range(0, iter_count, 1):
                aux_sufix = ''
                if i in sufix:
                    aux_sufix = sufix[i]
                if hours_counter == 1:
                    init = 0
                else:
                    init = hours_counter - 1
                list_hours.append(
                    [0, 0,
                     {'hour_production': str(1 + i) + aux_sufix + ' hora ' + (date_start + timedelta(hours=init)).strftime('%H:%M') + ' a ' +
                                         (date_start + timedelta(hours=hours_counter)).strftime('%H:%M')}])
                hours_counter += 1
                self.production_by_hours_ids = list_hours
            self._compute_plan_time()

    @api.multi
    @api.depends('attendance_id')
    def _compute_plan_time(self):
        for att in self:
            date_start = datetime.strptime(str(int(att.attendance_id.hour_from)), '%H')
            date_end = datetime.strptime(str(int(att.attendance_id.hour_to)), '%H')
            timedelta_diff = date_end - date_start
            att.plan_time = int(timedelta_diff.seconds / 3600)

    @api.model
    def create(self, vals):
        if 'production_by_hours_ids' in vals:
            no_extra_hr = 1
            for ph in vals['production_by_hours_ids']:
                if ph[2]['hour_production'] == 'Hora extra ':
                    ph[2]['hour_production'] += str(no_extra_hr)
                    no_extra_hr += 1
        return super(tecnolog_control_model, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'production_by_hours_ids' in vals:
            no_extra_hr = 1
            for ph in vals['production_by_hours_ids']:
                if ph[2] and 'hour_production' in ph[2]:
                    if ph[2]['hour_production'] == 'Hora extra ':
                        ph[2]['hour_production'] += str(no_extra_hr)
                        no_extra_hr += 1
        return super(tecnolog_control_model, self).write(vals)

class turno(models.Model):
    _name = 'process_control_tobacco.turno'
    _rec_name = 'turn'

    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", required=True, copy=True)
    active = fields.Boolean(default=True)




class production_by_hours(models.Model):
    _name = 'process_control_tobacco.production_by_hours'

    tecnolog_control_id = fields.Many2one(comodel_name="process_control_tobacco.tecnolog_control_model",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )

    def _default_hour_production(self):
        return 'Hora extra '

    hour_production = fields.Char(string='Horario', readonly=True, default=_default_hour_production)
    production_count = fields.Float(string='Producción (Kg)')

    @api.model
    def create(self, vals):
        return super(production_by_hours, self).create(vals)

    @api.onchange('hour_production')
    def _onchange_hour_production(self):
        if not self.hour_production:
            pass