# -*- coding: utf-8 -*-
from datetime import timedelta, datetime

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class tecnolog_control_model(models.Model):
    _name = 'process_control_primary.tecnolog_control_model'

    date = fields.Date(string="Fecha", required=True, copy=True)
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)
    day_char = fields.Char(string=u"Día", required=False, compute="_compute_day_char", store=True)
    turn = fields.Many2one(comodel_name="resource.calendar", string="Turno", domain=[('turn_process_control', '=', True)], required=True, copy=True)

    attendance_id = fields.Many2one('resource.calendar.attendance', string='Sesión', copy=True, required=True, )

    productive_line = fields.Many2one(comodel_name="process_control_primary.productive_line",
                                         string="Línea productiva",
                                         required=True, ondelete='cascade')
    productive_capacity = fields.Integer('Capacidad Productiva', required=True, default=3500)
    plan_time = fields.Integer('Tmpo. Plan(Horas)', required=True)


    interruptions = fields.One2many(comodel_name="process_control_primary.interruption", inverse_name="tec_control_model",
                                    string="Interrupciones", required=False, ondelete='cascade')



    production_in_production_system = fields.Float(readonly=True, compute="_production_in_production_system", store=True,

                                                   help="Muestra producción registraba en el sistema de producción.")

    execution_time = fields.Float('Tiempo Ejecución(Horas)', required=True)

    name = fields.Char(string="Nombre", required=False, compute='_calc_name')

    _sql_constraints = [('turn_in_date_uniq', 'unique(turn,date,productive_line,attendance_id)',
                         "Ya existe un modelo registrado para el turno (Linea) en la fecha seleccionada."),
                        ('attendance_in_productive_uniq', 'unique(date,productive_line,attendance_id)',
                         "Ya existe un modelo registrado para esa Linea en la fecha seleccionada.")]

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
            attendace_ids = self.env['resource.calendar.attendance'].search([('calendar_id.id', '=', self.turn.id)])
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

    @api.depends('turn', 'productive_line', 'date')
    def _production_in_production_system(self):
        for c_model in self:
            if c_model.turn and c_model.productive_line and c_model.date:
                connexion = self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)
                connexion.ensure_one()

                if connexion:
                    try:
                        cursor = connexion.connect().cursor()
                        if c_model.productive_line.codigo == 'LCS':
                            query = """SELECT SUM(hebra) FROM hb_produccion WHERE id_turno = %d and fecha = '%s'""" % (self.turn.sgp_turn_id, self.date)

                        else:
                            query = """SELECT SUM(repeso) from view_hb_rpt_resumen_parte_1 WHERE id_turno = %d and fecha = '%s'""" % (self.turn.sgp_turn_id, self.date)


                        cursor.execute(query)

                        for row in cursor:
                            c_model.production_in_production_system = row[0]
                    except Exception, e:
			print(e)
                        pass

    @api.onchange('turn', 'productive_line', 'date')
    def _onchange_in_production_system(self):
        for c_model in self:
            if c_model.turn and c_model.productive_line and c_model.date:
                connexion = self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)
                connexion.ensure_one()

                if connexion:
                    try:
                        cursor = connexion.connect().cursor()
                        if c_model.productive_line.codigo == 'LCS':
                            query = """SELECT SUM(hebra) FROM hb_produccion WHERE id_turno = %d and fecha = '%s'""" % (self.turn.sgp_turn_id, self.date)

                        else:
                            query = """SELECT SUM(repeso) from view_hb_rpt_resumen_parte_1 WHERE id_turno = %d and fecha = '%s'""" % (self.turn.sgp_turn_id, self.date)


                        cursor.execute(query)

                        for row in cursor:
                            c_model.production_in_production_system = row[0]
                    except Exception, e:
                        pass