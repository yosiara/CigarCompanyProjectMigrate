# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date


class Candidato(models.Model):
    _inherit = 'hr.applicant'

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

    @api.model
    def _get_default_country(self):
        return 52

    @api.model
    def _get_default_municipality(self):
        return self.env['l10n_cu_base.municipality'].search([('name', '=', 'Holguín')], limit=1).id

    @api.model
    def _get_default_provincia(self):
        return self.env['res.country.state'].search([('name', '=', 'Holguín')], limit=1).id

    name = fields.Char('Nombre del candidato', size=60, required=True)

    partner_name = fields.Char(string='Nombre del candidato', store=True, compute='_compute_name')

    @api.depends('name')
    def _compute_name(self):
        for candidato in self:
            self.partner_name = self.name

    fecha_inicio_proceso = fields.Date('Fecha de inicio del Proceso',required=True)
    ci = fields.Char(string='Carnet de Identidad', size=11, required=True)
    direccion_particular = fields.Char(string='Dirección Particular',required=True)
    municipality_id = fields.Many2one('l10n_cu_base.municipality', string='Municipio',
                                      default=_get_default_municipality)
    municipality_name = fields.Char('Municipio', related='municipality_id.name')
    reparto_id = fields.Many2one('app_seleccion.reparto',string='Reparto')
    state_id = fields.Many2one('res.country.state', string='Provincia', ondelete='restrict', default=_get_default_provincia)
    country_id = fields.Many2one('res.country', string='País', ondelete='restrict', default=_get_default_country)
    applicant_email = fields.Char('Correo Electrónico')
    applicant_phone = fields.Char('Teléfono')
    applicant_mobile = fields.Char('Móvil')
    ubicacion_laboral_actual = fields.Char(string='Ubicación Laboral Actual', size=50)
    direccion_laboral_actual = fields.Char(string='Dirección Laboral Actual', size=50)
    school_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='Nivel Escolar')
    degree_id = fields.Many2one('l10n_cu_hlg_uforce.degree', string='Carrera')
    calificacion_name = fields.Char('Calificaciación',related='degree_id.name',store=True)
    experiencia_laboral = fields.Integer(string='Experiencia Laboral', size=2)
    curso_habilitacion = fields.Many2one('app_seleccion.curso', string='Curso de habilitación')
    nombre_curso = fields.Char('Curso de habilitación', related='curso_habilitacion.name',store=True)
    nombre_trabajo = fields.Char('hr.job', related='job_id.name',store=True)
    area = fields.Many2one('app_seleccion.area', string='Área para la que se procesa', ondelete='set null')
    nombre_area = fields.Char('Área', related='area.name', store=True)
    area_code = fields.Char('Código de área', related='area.code', store=True)
    estado = fields.Selection([('proceso', 'En Proceso'), ('aprobado', 'Aprobado para Puesto de Trabajo'),
                               ('reserva', 'Reserva'), ('curso', 'Aprobado para Curso'),
                               ('rechazado', 'No Aprobado')],
                              string='Estado de la Solicitud', default='proceso')

    estudent_id = fields.Many2one('app_seleccion.estudiante', string="Estudiante",ondelete='set null')

    stage_name = fields.Char('Etapa',related='stage_id.name')


    @api.depends('estado')
    def get_estudent(self):
        if self.estado == 'curso':
            self.estudiante = True
        else:
            self.estudiante = False


    year = fields.Integer('Año de la solicitud', compute='_set_year',store=True)
    @api.depends('fecha_inicio_proceso')
    def _set_year(self):
        if self.fecha_inicio_proceso:
            fecha_hoy = self.fecha_inicio_proceso
            year = fecha_hoy.split('-')
            year = year[0]
            self.year = int(year)
        else:
            fecha_hoy = fields.Date.today()
            year = fecha_hoy.split('-')
            year = year[0]
            self.year = int(year)


    mes = fields.Char('Mes de la solicitud', compute='_set_mes',store=True)
    @api.depends('fecha_inicio_proceso')
    def _set_mes(self):
        if self.fecha_inicio_proceso:
            fecha_hoy = self.fecha_inicio_proceso
            mes = fecha_hoy.split('-')
            mes = mes[1]
            self.mes = mes
        else:
            fecha_hoy = fields.Date.today()
            mes = fecha_hoy.split('-')
            mes = mes[1]
            self.mes = mes

    mes_nombre = fields.Char('Mes de la solicitud', compute='_set_mes_nombre',store=True)
    @api.depends('fecha_inicio_proceso')
    def _set_mes_nombre(self):
        if self.fecha_inicio_proceso:
            fecha_hoy = self.fecha_inicio_proceso
            mes = fecha_hoy.split('-')
            mes = mes[1]
            self.mes_nombre = self.get_nombre_mes(mes)
        else:
            fecha_hoy = fields.Date.today()
            mes = fecha_hoy.split('-')
            mes = mes[1]
            self.mes_nombre = self.get_nombre_mes(mes)


    # determinar el sexo a partir del penultimo digito de los ci de 11
    sexo = fields.Char(string='Sexo', store=True, compute='_compute_sexo')

    @api.depends('ci')
    def _compute_sexo(self):
        if len(self.ci) == 11:
            if int(self.ci[9]) % 2 == 0:
                self.sexo = 'Masculino'
            else:
                self.sexo = 'Femenino'

    # determinar la edad a partir de los 6 primeros digitos de los ci de 11
    edad = fields.Char(string='Edad', store=True, compute='_compute_edad')

    @api.depends('ci')
    def _compute_edad(self):
        if len(self.ci) == 11:
            fecha_hoy = fields.Date.today()
            arreglo_fechas = fecha_hoy.split('-')
            arr = arreglo_fechas[0]
            year_actualr = arr[2:]
            year_actual = int(arreglo_fechas[0])
            mes_actual = int(arreglo_fechas[1])
            dia_actual = int(arreglo_fechas[2])

            # determinar fecha nacimiento del ci
            year_candidato = self.ci[0:2]
            mes_candidato = self.ci[2:4]
            dia_candidato = self.ci[4:6]

            if int(year_candidato) > int(year_actualr):
                year_candidato = 1900 + int(year_candidato)
            else:
                year_candidato = 2000 + int(year_candidato)

            if int(mes_candidato) < mes_actual:
                self.edad = year_actual - year_candidato
            elif int(mes_candidato) == mes_actual and int(dia_candidato) <= dia_actual:
                self.edad = year_actual - year_candidato
            elif int(mes_candidato) == mes_actual and int(dia_candidato) > dia_actual:
                self.edad = (year_actual - year_candidato) - 1
            else:
                self.edad = (year_actual - year_candidato) - 1




    # validar que se introduzca el puesto de trabajo
    @api.constrains('job_id', 'curso_habilitacion')
    def _check_job(self):
        if not self.job_id and not self.curso_habilitacion:
            raise ValidationError(_("Debe escoger el Puesto de Trabajo o el Curso de Habilitacion!!"))

    # validar que se introduzca un ci válido antes de enviar
    @api.constrains('ci')
    def _check_ci(self):
        if not self.ci:
            raise ValidationError(_("Debe escribir el Carnet de Identidad !!"))
        else:
            ci = str(self.ci)
            if not ci.isdigit():
                raise ValidationError(_("Debe escribir un Carnet de Identidad válido!!"))
            elif len(self.ci) > 11 or len(self.ci) < 11:
                raise ValidationError(
                    _("El Carnet de Identidad debe tener 11 digitos, debe escribir un Carnet de Identidad válido !!"))

    # validar el campo experiencia laboral
    @api.constrains('experiencia_laboral')
    def _check_experiencia_laboral(self):
        experiencia_laboral = str(self.experiencia_laboral)
        if not experiencia_laboral.isdigit():
            raise ValidationError(_("El campo experiencia laboral solo admite números enteros de 1 o 2 cifras!!"))

    sequence_id = fields.Char('Sequence', readonly=True)

    @api.multi
    def action_get_created_estudent(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('app_seleccion', 'open_view_estudent_list')
        action['res_id'] = self.mapped('estudent_id').ids[0]
        return action


    #crear estudiante
    @api.multi
    def create_estudent_from_applicant(self):

        estudent = self.env['app_seleccion.estudiante'].create({'name': self.name,
                                                                 'ci': self.ci,
                                                                'curso': self.curso_habilitacion.id,

                                                                })

        # creo el registro de evaluaciones para los cursos
        aspectos = self.env['app_seleccion.aspecto'].search([])
        for element in aspectos:
            aspecto_id = element.id
            eval = self.env['app_seleccion.evaluacion']
            eval.create({'estudiante_id': estudent.id, 'aspecto_evaluar_id': aspecto_id})

        for applicant in self:
            applicant.write({'estudent_id': estudent.id})



        estudent_action = self.env.ref('app_seleccion.open_view_estudent_list')
        dict_act_window = estudent_action.read([])[0]
        if estudent:
            dict_act_window['res_id'] = estudent.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window




    @api.model
    @api.multi
    def create(self, vals):
        seq = self.env['ir.sequence'].get('seq.seq') or '/'
        vals['sequence_id'] = seq

        candidato = super(Candidato, self).create(vals)

        return candidato

    sequence_name = fields.Char('Código de Solicitud', readonly=True, compute='compute_consec', store=True)

    @api.depends('sequence_id', 'area_code')
    @api.one
    def compute_consec(self):
        year_actual = fields.Date.today()
        year_actual = year_actual.split('-')
        year_actual = int(year_actual[0])
        if self.year == year_actual:
            self.sequence_name = self.area_code + '-' + self.sequence_id
        else:
            total = self.env['hr.applicant'].search_count([('area_code','=',self.area_code),('year','=',self.year)])
            # seq_id = self.sequence_id
            # seq_id = seq_id.split('/')
            # seq_id = seq_id[0]
            seq_id = total
            seq_id = tools.ustr(seq_id).zfill(3)
            seq_id = seq_id+'/'+tools.ustr(self.year)
            self.sequence_name = self.area_code + '-'+ seq_id

    # crear empleado, sobrescribe el metodo del modelo hr.recruitment
    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:
            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if (applicant.job_id and (applicant.partner_name or contact_name)) or (
                applicant.curso_habilitacion and (applicant.partner_name or contact_name)):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})

                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                                           'job_id': applicant.job_id.id,
                                                           'aprobado_en_seleccion': True,
                                                           'direccion_particular': applicant.direccion_particular,
                                                           'ci': applicant.ci,
                                                           'address_home_id': address_id,
                                                           'department_id': applicant.department_id.id or False,
                                                           'area_id': applicant.area.id or False,
                                                           'degree_id': applicant.degree_id.id,
                                                           'curso': applicant.curso_habilitacion.id or False,
                                                           'country_id': applicant.country_id.id,
                                                           # 'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                                           'private_email': applicant.applicant_email or False,
                                                           'private_mobile': applicant.applicant_mobile or False,
                                                           'private_phone': applicant.applicant_phone or False
                                                           })
                # creo el registro de evaluaciones para los cursos
                aspectos = self.env['app_seleccion.aspecto'].search([])
                for element in aspectos:
                    aspecto_id = element.id
                    evaluacion = 'N'
                    eval = self.env['app_seleccion.evaluacion']
                    eval.create(
                        {'empleado_id': employee.id, 'aspecto_evaluar_id': aspecto_id, 'evaluacion': evaluacion})

                applicant.write({'emp_id': employee.id})
                applicant.job_id.message_post(
                    body=_(
                        'New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window

