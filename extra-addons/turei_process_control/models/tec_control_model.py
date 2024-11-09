# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class tecnolog_control_model(models.Model):
    _name = 'turei_process_control.tecnolog_control_model'
    _translate = False

    date = fields.Date(string="Fecha", required=True, copy=True, default=fields.Date.today)
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)
    day_char = fields.Char(string=u"Día", required=False, compute="_compute_day_char", store=True)
    turn = fields.Many2one(comodel_name="resource.calendar", domain=[('turn_process_control', '=', True)], string="Turno", required=True, copy=True, default=0)

    attendance_id = fields.Many2one('resource.calendar.attendance', string='Sesión', copy=True, default=0)

    productive_section = fields.Many2one(comodel_name="turei_process_control.productive_section",
                                         string="Modulo",
                                         required=True, ondelete='cascade')
    productive_capacity = fields.Integer('Capacidad Productiva', required=True)
    plan_time = fields.Integer('Tmpo. Plan(Horas)', required=True)

    def _get_default_tec_model_type(self):
        if self.productive_section:
            self.tec_model_type = self.productive_section.tec_model_type

    tec_model_type = fields.Selection(string="Documento/control", default=_get_default_tec_model_type,
                                      selection=[('mod', 'Módulo'), ('mod1', 'Módulo 1')])

    interruptions = fields.One2many(comodel_name="turei_process_control.interruption", inverse_name="tec_control_model",
                                    string="Interrupciones", required=False, ondelete='cascade')

    production_by_hours_ids = fields.One2many(comodel_name="turei_process_control.production_by_hours",
                                              inverse_name="tecnolog_control_id",
                                              string="Produccion Horaria", required=False)

    production_in_production_system = fields.Float(string="Prod. Sistema prod.", readonly=True,
                                                   compute="get_production_in_production_system",
                                                   help="Muestra producción registraba en el sistema de producción.")

    production_in_proccess_control = fields.Float(string="Prod calculada en el sistema.", readonly=True, store=True,
                                                  compute='_compute_total_prod')

    rechazo_amf = fields.One2many(comodel_name="turei_process_control.rechazo_amf",
                                  inverse_name="tecnolog_control_id",
                                  string="Rechazo de las AMF", required=False)

    rechazo_nano_sbo_src = fields.One2many(comodel_name="turei_process_control.rechazo_mod1",
                                           inverse_name="tecnolog_control_id",
                                           string="Rechazo 'NANO', 'SBO', 'SRC'", required=False)

    name = fields.Char(string="Nombre", required=False, compute='_calc_name')

    _sql_constraints = [('turn_in_date_uniq', 'unique(turn,date,productive_section,attendance_id)',
                         "Ya existe un modelo registrado para el turno (Sesión) en la fecha seleccionada."),
                        ('attendance_in_productive_uniq', 'unique(date,productive_section,attendance_id)',
                         "Ya existe un modelo registrado para esa Sesión en la fecha seleccionada.")]

    @api.model
    def default_get(self, fields):
        res = super(tecnolog_control_model, self).default_get(fields)
        rec_last = self.search([], order='id desc', limit=1)
        if rec_last:
            res["date"] = rec_last.date
            res["turn"] = int(rec_last.turn)
            res["attendance_id"] = int(rec_last.attendance_id)
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

    @api.constrains('production_by_hours_ids')
    def check_production_by_hours_ids(self):
        #if self.production_in_production_system == self.production_in_proccess_control == 0:
            #pass
            #raise ValidationError('Producción registrada no puede ser 0')
        if self.production_in_production_system != self.production_in_proccess_control:
            self.env.user.notify_info(
                'Producción registrada no coincide con la registrada en el sistema de producción.')
            # raise ValidationError('Producción registrada no coincide con la registrada en el sistema de producción.')

    @api.depends('turn', 'productive_section', 'date')
    def get_production_in_production_system(self):
        if self.turn and self.productive_section and self.date:
            connexion = self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)
            connexion.ensure_one()
            res = []
            self.production_in_production_system = 0
            if connexion:
                try:
                    cursor = connexion.connect().cursor()
                    query = """SELECT SUM(cantidad_producida) FROM pt_produccion_terminada
    WHERE id_modulo = %d AND id_turno = %d and fecha = '%s'""" % (
                        int(self.productive_section.production_id), self.turn.sgp_turn_id, self.date)
                    cursor.execute(query)
                    for row in cursor:
                        self.production_in_production_system = row[0]
                except Exception, e:
                    pass

    @api.multi
    def _calc_name(self):
        for doc in self:
            doc.name = "Documento de control"

    @api.onchange('turn')
    def get_attendance_ids(self):
        if self.turn:
            attendace_ids = self.env['resource.calendar.attendance'].search([('calendar_id.id', '=', self.turn.id)])
            print(len(attendace_ids))
            # self.attendance_id = False
            return {'domain': {'attendance_id': [('id', 'in', attendace_ids.ids)]}}
        return {'domain': {'attendance_id': [('calendar_id', 'in', [])]}}


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
                list_hours.append(
                    [0, 0,
                     {'hour_production': str(1 + i) + aux_sufix + ' hora ' + date_start.strftime('%H:%M') + ' a ' +
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

    @api.onchange('productive_section')
    def _onchange_productive_section(self):
        if self.productive_section:
            self.production_by_hours_ids = False
            self.interruptions = False
            self.rechazo_amf = False
            self.rechazo_nano_sbo_src = False
            self.tec_model_type = self.productive_section.tec_model_type
            self.productive_capacity = self.productive_section.get_efficiency_plan().productive_capacity
            self._onchange_attendance_id()

            list_lines = []
            for line in self.productive_section.productive_line_ids:
                if self.productive_section.tec_model_type == 'mod':
                    machine_type_id = self.env['turei_process_control.machine_type'].search([('name', '=', 'AMF')])
                    machine_ids = line.productive_line.machine_ids.search([('machine_type_id', '=', machine_type_id.id),
                                                                       ('id', 'in',
                                                                        line.productive_line.machine_ids.ids)], limit=1)
                    list_lines.append([0, 0, {
                        'productive_line_id': line.id,
                        'machine_id': machine_ids.id
                    }])
                    self.rechazo_amf = list_lines
                # else:
                #     list_lines.append([0, 0, {
                #         'productive_line_id': line.id,
                #     }])
                #     self.rechazo_nano_sbo_src = list_lines


    @api.multi
    @api.depends('production_by_hours_ids.production_count')
    def _compute_total_prod(self):
        for mod in self:
            if mod.production_by_hours_ids:
                total = 0
                for prod in mod.production_by_hours_ids:
                    total += prod.production_count
                mod.production_in_proccess_control = total

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


class production_by_hours(models.Model):
    _name = 'turei_process_control.production_by_hours'

    tecnolog_control_id = fields.Many2one(comodel_name="turei_process_control.tecnolog_control_model",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )

    def _default_hour_production(self):
        return 'Hora extra '

    hour_production = fields.Char(string='Horario', readonly=True, default=_default_hour_production)
    production_count = fields.Float(string='Produccion (Cajones)')

    @api.model
    def create(self, vals):
        return super(production_by_hours, self).create(vals)

    @api.onchange('hour_production')
    def _onchange_hour_production(self):
        if not self.hour_production:
            pass


class rezacho_amf(models.Model):
    _name = 'turei_process_control.rechazo_amf'

    productive_line_id = fields.Many2one('turei_process_control.productive_section_lines', string='Líneas Productivas')
    machine_id = fields.Many2one('turei_process_control.machine', 'Máquina',
                                 # dominio vacio hasta que se escoja una seccion productiva
                                 domain=[('id', 'in', [])])
    machine_type_id = fields.Many2one('turei_process_control.machine_type', string='Tipo de máquina',
                                      related='machine_id.machine_type_id')

    rechazo_en_cajetijas = fields.Integer('Rechazo en cajetillas')
    produccion_en_cajones = fields.Float('Produción en cajones')
    tecnolog_control_id = fields.Many2one(comodel_name="turei_process_control.tecnolog_control_model",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )
    tec_model_type = fields.Selection(string="Documento/control",
                                      selection=[('mod', 'Módulo')], readonly=True, default='mod')

    @api.multi
    @api.onchange('productive_line_id')
    def _onchange_productive_line(self):
        for psc in self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', psc.productive_line.machine_ids.ids),
                                              ('machine_type_id.name', '=', 'AMF')]}}
        return {'domain': {'machine_id': [('id', 'in', [])]}}

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids),
                                              ('machine_type_id.name', '=', 'AMF')]}}


class rechazo_modulo1(rezacho_amf):
    _name = 'turei_process_control.rechazo_mod1'

    productive_line_id = fields.Many2one('turei_process_control.productive_section_lines', string='Líneas Productivas')
    machine_id = fields.Many2one('turei_process_control.machine', 'Máquina',
                                 # dominio vacio hasta que se escoja una seccion productiva
                                 domain=[('id', 'in', [])])
    machine_type_id = fields.Many2one('turei_process_control.machine_type', string='Tipo de máquina',
                                      related='machine_id.machine_type_id')

    machine_type_name = fields.Char("Machine Type name", related='machine_type_id.name')

    rechazo_en_cajetillas = fields.Integer('Rechazo en cajetillas')
    rechazo_en_cigarrillos = fields.Integer('Rechazo en cigarrillos')
    produccion_en_cajones = fields.Float('Produción en cajetillas')
    produccion_en_cigarrillos = fields.Integer('Produción en cigarrillos')
    tecnolog_control_id = fields.Many2one(comodel_name="turei_process_control.tecnolog_control_model",
                                          string="Modelo Control", ondelete='cascade',
                                          required=True, )

    tec_model_type = fields.Selection(string="Documento/control",
                                      selection=[('mod1', 'Módulo')], required=True, readonly=True, default='mod1')

    @api.multi
    @api.onchange('productive_line_id')
    def _onchange_productive_line(self):
        for psc in self.productive_line_id:
                return {'domain': {'machine_id': [('id', 'in', psc.productive_line.machine_ids.ids),
                                                  ('machine_type_id.name', 'in', ['NANO', 'SBO', 'SRC'])]}}
        return {'domain': {'machine_id': [('id', 'in', [])]}}

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.productive_line_id:
            return {'domain': {'machine_id': [('id', 'in', self.productive_line_id.productive_line.machine_ids.ids),
                                                  ('machine_type_id.name', 'in', ['NANO', 'SBO', 'SRC'])]}}
