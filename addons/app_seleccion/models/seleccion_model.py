# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from datetime import timedelta, datetime, date

class TipoEstructura(models.Model):
    _name = 'app_seleccion.tipo_estructura'
    name = fields.Char(string='Estructura',sise=50, required=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Ya existe un tipo de estructura con ese nombre!!')]

class Area(models.Model):
    _name = "app_seleccion.area"

    name = fields.Char(string='Area',sise=50, required=True)
    code = fields.Char(string='Código',sise=5, required=True)
    tipo_estructura = fields.Many2one('app_seleccion.tipo_estructura',string='Tipo de Estructura')

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Ya existe un Área con ese nombre!!')]

    #validar que se escoja un area
    @api.constrains('tipo_estructura')
    def _check_tipo(self):
        if not self.tipo_estructura:
            raise ValidationError(_("Debe escoger un tipo de Estructura: UEB o Área de Regulación y Control!!"))




class SolicitudExpertos(models.Model):
    _name = 'app_seleccion.solicitud_expertos'



    @staticmethod
    def get_nombre_mes(mes):
        if mes == '01':
            return 'enero'
        elif mes == '02':
            return 'febrero'
        elif mes == '03':
            return 'marzo'
        elif mes == '04':
            return 'abril'
        elif mes == '05':
            return 'mayo'
        elif mes == '06':
            return 'junio'
        elif mes == '07':
            return 'julio'
        elif mes == '08':
            return 'agosto'
        elif mes == '09':
            return 'septiembre'
        elif mes == '10':
            return 'octubre'
        elif mes == '11':
            return 'noviembre'
        elif mes == '12':
            return 'diciembre'

    sequence_id = fields.Char('Sequence', readonly=True)
    numero_solicitud = fields.Char('Número de Solicitud',required=True)
    name = fields.Char(compute='_set_name')

    @api.depends('numero_solicitud')
    def _set_name(self):
        if self.numero_solicitud:
            self.name = self.numero_solicitud

    fecha_solicitud = fields.Date('Fecha de Solicitud',required=True)
    fecha_fin = fields.Date('Fecha de Resultados del Comité de Expertos')

    job_id = fields.Many2one('hr.job', string='Puesto de Trabajo',track_visibility='onchange')
    nombre_trabajo = fields.Char('Nombre trabajo',related='job_id.name',store=True)
    curso_id = fields.Many2one('app_seleccion.curso',string='Curso de Habilitación',track_visibility='onchange')
    nombre_curso = fields.Char('Nombre curso',related='curso_id.name',store=True)


    estado = fields.Char('Estado',compute='_set_estado',store=True)

    @api.depends('fecha_fin')
    def _set_estado(self):
        if self.fecha_fin:
            self.estado = 'Finalizado'
        else:
            self.estado = 'Iniciado'



    year = fields.Char(string='Año',compute='_set_year',store=True)
    @api.depends('fecha_solicitud')
    def _set_year(self):
        fecha = self.fecha_solicitud
        fecha = fecha.split('-')
        self.year = fecha[0]


    applicant_ids = fields.Many2many('hr.applicant',string='Candidatos en Proceso',track_visibility='onchange')

    employee_ids = fields.Many2many('hr.employee',string='Candidatos de Fuente Interna',track_visibility='onchange')


    @api.onchange('job_id')
    def get_applicants(self):
         self.applicant_ids = False

         if self.job_id:
             return {'domain': {'applicant_ids': [('job_id', 'in', self.job_id.ids),('estado','=','proceso')]}}


    @api.onchange('curso_id')
    def get_applicants_by_curso(self):
         self.applicant_ids = False

         if self.curso_id:
             return {'domain': {'applicant_ids': [('curso_habilitacion', 'in', self.curso_id.ids),('estado','=','proceso')]}}

    # validar que se introduzca el puesto de trabajo o el curso
    @api.constrains('job_id', 'curso_id')
    def _check_job_curso(self):
        if not self.job_id and not self.curso_id:
            raise ValidationError(_("Debe escoger el Puesto de Trabajo o el Curso de Habilitacion!!"))
        elif self.job_id and self.curso_id:
            raise ValidationError(_("Debe escoger el Puesto de Trabajo o el Curso de Habilitacion, solo uno de los dos campos !!"))


    #validar que no se repita el numero de solicitud
    @api.constrains('numero_solicitud')
    def _check_numero(self):
        year_actual = fields.Date.today()
        year_actual = year_actual.split('-')
        year_actual = year_actual[0]

        numero = self.env['app_seleccion.solicitud_expertos'].search_count([('numero_solicitud','=',self.numero_solicitud),('year','=',year_actual)])
        if numero > 0:
            raise ValidationError(_("Ya existe una Solicitud con ese número !!"))



    #validar que la fecha de terminación del comite sea mayor que la de solicitud
    @api.constrains('fecha_fin','fecha_solicitud')
    def check_fechas(self):
        if self.fecha_fin and self.fecha_solicitud > self.fecha_fin:
            raise ValidationError(_("La Fecha de Resultado del Comité no puede ser anterior a la de Solicitud !!"))



    tiempo_en_comite = fields.Integer('Días en Comité de Expertos',compute='_set_tiempo_expertos',store=True)

    @api.depends('fecha_solicitud','fecha_fin')
    def _set_tiempo_expertos(self):
        if not self.fecha_fin:
            tiempo = datetime.strptime(fields.Date.today(),'%Y-%m-%d') - datetime.strptime(self.fecha_solicitud,'%Y-%m-%d')
            self.tiempo_en_comite = tiempo.days
        else:
            tiempo = datetime.strptime(self.fecha_fin,'%Y-%m-%d') - datetime.strptime(self.fecha_solicitud,'%Y-%m-%d')
            self.tiempo_en_comite = tiempo.days

    mes_experto = fields.Char('Mes Comite Expertos',compute='_get_mes_experto',store=True)

    @api.depends('fecha_solicitud')
    def _get_mes_experto(self):
         mes = self.fecha_solicitud
         mes = mes.split('-')
         mes = mes[1]
         self.mes_experto = mes

    mes_experto_nombre = fields.Char('Mes Comite Expertos',compute='_get_mes_experto_nombre',store=True)
    @api.depends('mes_experto')
    def _get_mes_experto_nombre(self):
        if self.mes_experto:
            mes = self.fecha_solicitud
            mes = mes.split('-')
            mes = mes[1]
            self.mes_experto_nombre = self.get_nombre_mes(mes)

    @api.model
    @api.multi
    def create(self, vals):
        seq = self.env['ir.sequence'].get('seq.solicitud') or '/'
        vals['sequence_id'] = seq

        solicitud = super(SolicitudExpertos, self).create(vals)

        return solicitud

    #enviar email con solicitudes a punto de llegar a los 10 dias
    @api.model
    def send_email_notification(self):
        email_to = ''
        dicc = {
            'email_to': email_to
        }

        solicitudes_ids = self.env['app_seleccion.solicitud_expertos'].search([('estado','=','iniciado'),('tiempo_en_comite','>',7)])
        solicitudes = []

        for solicitud in solicitudes_ids:
            solicitudes.append((solicitud.numero_solicitud,solicitud.fecha))

        if len(solicitudes):
            template = self.env.ref('app_seleccion.mail_template_data_notification_comite_expertos')
            template.with_context(dbname=self._cr.dbname, solicitud=solicitudes).send_mail(self.id, force_send=True,
                                                                                         email_values=dicc)

        return True


class Reparto(models.Model):
    _name = 'app_seleccion.reparto'

    name = fields.Char('Reparto o Comunidad')



