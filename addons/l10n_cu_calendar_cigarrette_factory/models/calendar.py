# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, relativedelta
import logging
import pytz
import re
import time
from dateutil import parser
from dateutil import rrule

from datetime import datetime, date, timedelta
from odoo.addons.calendar.models.calendar import VIRTUALID_DATETIME_FORMAT
from odoo.addons.calendar.models.calendar import calendar_id2real_id, Meeting as OdooMeeting

_logger = logging.getLogger(__name__)


class SistematizadoresList(models.Model):
    _name = 'l10n_cu_calendar.sistematizadores_list'

    name = fields.Many2one('res.users', string='Sistematizador(a)', required=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            # Buscar la company a la que pertenece al usuario
            self.company_id = self.name.company_id.id


class Meeting(models.Model):
    _inherit = 'calendar.event'
    _order = 'start ASC, hora_gral ASC'

    notifica_puntualizacion_sist = fields.Boolean(string='Notificar Sistematizadores')
    hora_gral = fields.Char(string='Hora Inicio', compute='_compute_hora_gral')
    dia = fields.Char(string='Dia', compute='_compute_dia')

    @api.onchange('name')
    def _onchange_name(self):
        short_name = ''
        if self.name:
            name_array = self.name.split()
            for na in name_array:
                if len(na) > 3:
                    short_name += na[0:3] + '.'
        self.short_name = short_name

    @api.multi
    def _compute_hora_gral(self):
        for record in self:
                hora_gral = ''
                if record.allday:
                    record.hora_gral = 'T/D'
                else:
                    # Hay que ubicar en el meridiano y demas las horas de inicio y fin para que sea la adecuada
                    if record.start and record.stop:
                        # Trabajo con el meridiano
                        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                        startdate = datetime.strptime(record.start, DEFAULT_SERVER_DATETIME_FORMAT)
                        startdate = pytz.UTC.localize(startdate)  # Add "+hh:mm" timezone
                        startdate = startdate.astimezone(timezone)

                        calendar_start = datetime.strptime(record.start, DEFAULT_SERVER_DATETIME_FORMAT)
                        calendar_start = pytz.UTC.localize(calendar_start)  # Add "+hh:mm" timezone
                        calendar_start = calendar_start.astimezone(timezone)

                        stopdate = datetime.strptime(record.stop, DEFAULT_SERVER_DATETIME_FORMAT)
                        stopdate = pytz.UTC.localize(stopdate)  # Add "+hh:mm" timezone
                        stopdate = stopdate.astimezone(timezone)

                        calendar_stop = datetime.strptime(record.stop, DEFAULT_SERVER_DATETIME_FORMAT)
                        calendar_stop = pytz.UTC.localize(calendar_stop)  # Add "+hh:mm" timezone
                        calendar_stop = calendar_stop.astimezone(timezone)

                        hora_inicio = ''
                        hora_fin = ''
                        hora_inicio_text = fields.Datetime.to_string(startdate)[11:16]
                        hora_fin_text = fields.Datetime.to_string(stopdate)[11:16]

                        if hora_inicio_text[0:2] >= '12':
                            if hora_inicio_text[0:2] == '13':
                                hora_inicio = '01:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '14':
                                hora_inicio = '02:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '15':
                                hora_inicio = '03:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '16':
                                hora_inicio = '04:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '17':
                                hora_inicio = '05:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '18':
                                hora_inicio = '06:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '19':
                                hora_inicio = '07:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '20':
                                hora_inicio = '08:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '21':
                                hora_inicio = '09:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '22':
                                hora_inicio = '10:' + hora_inicio_text[3:5] + ' PM'
                            elif hora_inicio_text[0:2] == '23':
                                hora_inicio = '11:' + hora_inicio_text[3:5] + ' PM'
                        else:
                            hora_inicio = hora_inicio_text + ' AM'

                        if hora_fin_text[0:2] > '12':
                            if hora_fin_text[0:2] == '13':
                                hora_fin = '01:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '14':
                                hora_fin = '02:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '15':
                                hora_fin = '03:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '16':
                                hora_fin = '04:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '17':
                                hora_fin = '05:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '18':
                                hora_fin = '06:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '19':
                                hora_fin = '07:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '20':
                                hora_fin = '08:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '21':
                                hora_fin = '09:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '22':
                                hora_fin = '10:' + hora_fin_text[3:5] + ' PM'
                            elif hora_fin_text[0:2] == '23':
                                hora_fin = '11:' + hora_fin_text[3:5] + ' PM'
                        else:
                            hora_fin = hora_fin_text + ' AM'

                        # hora_inicio = hora_inicio_text
                        # hora_fin = hora_fin_text

                        hora_gral = hora_inicio + ' - ' + hora_fin
                        record.hora_gral = hora_gral

    @api.multi
    def _compute_dia(self):
        for record in self:
            dia = ''
            if record.start:
                day_week_string = ''
                day_week = fields.Date.from_string(record.start).weekday()
                if day_week == 1:
                    day_week_string = 'Dom'
                elif day_week == 2:
                    day_week_string = 'Lun'
                elif day_week == 3:
                    day_week_string = 'Mar'
                elif day_week == 4:
                    day_week_string = 'Mie'
                elif day_week == 5:
                    day_week_string = 'Jue'
                elif day_week == 6:
                    day_week_string = 'Vie'
                elif day_week == 7:
                    day_week_string = 'Sab'

                dia = day_week_string + ' - ' + record.start[8:10]
            record.dia = dia

    def write(self, values):
        for record in self:
            if record.notifica_puntualizacion_sist:
                    # Si esta marcado y hay cambios en los campos de puntualizacion se notifica por correo a las
                    #  sistematizadoras.
                    lista_sist = self.env['l10n_cu_calendar.sistematizadores_list'].search([])
                    for sist in lista_sist:
                        notif = False
                        for participa in record.partner_ids:
                            if participa.company_id.id == sist.company_id.id:
                                notif = True
                        if notif:
                            mail_object = self.env['mail.mail']
                            email_content = {
                                'email_from': 'Sistema de Gestion de Direccion (UEB Produccion) <sistemas@turei.co.cu>',
                                'email_to': sist.name.partner_id.email,
                                'subject': "Cambios en Plan de Trabajo",
                                'body_html': (
                                        ('<html>La tarea "%s", ha sido modificada en fecha, hora o lugar donde se realiza. '
                                         'Revise el plan de trabajo para que compruebe los cambios. Gracias</html>') % self.name),
                                'subtype': 'html'
                            }
                            id_message = mail_object.create(email_content)
                            id_message.send()
                        
        return super(Meeting, self).write(values)

