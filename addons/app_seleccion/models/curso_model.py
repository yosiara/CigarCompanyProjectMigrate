# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class Aspecto(models.Model):
    _name = 'app_seleccion.aspecto'

    name = fields.Char(string='Aspecto',size=80, required=True)
    
    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Ya existe un aspecto con ese nombre!!')]

    #validar que se introduzca el aspecto
    @api.constrains('name')
    def _check_aspecto(self):
        if not self.name:
            raise ValidationError(_("Debe escribir el nombre del Aspecto a Evaluar!!"))


class Curso(models.Model):
    _name = 'app_seleccion.curso'

    name = fields.Char(string='Curso',size=80, required=True)

    _sql_constraints = [
        ('name_uniq',
         'UNIQUE (name)',
         'Ya existe un curso con ese nombre!!')]

    #validar que se introduzca el curso
    @api.constrains('name')
    def _check_curso(self):
        if not self.name:
            raise ValidationError(_("Debe escribir el nombre del Curso de Habilitacion!!"))


class Evaluacion(models.Model):
    _name = 'app_seleccion.evaluacion'


    estudiante_id = fields.Many2one('app_seleccion.estudiante',string='Estudiante', ondelete='cascade')
    #curso_id = fields.Many2one('hr.employee', related='empleado_id.curso',string='Curso')

    aspecto_evaluar_id = fields.Many2one('app_seleccion.aspecto',string='Aspecto a evaluar',ondelete='cascade')

    evaluacion = fields.Integer(string='Evaluación',size=3)

    #valida que no se repitan aspectos
    _sql_constraints = [
        ('aspecto_uniq',
         'UNIQUE (estudiante_id,aspecto_evaluar_id)',
         'Existen aspectos repetidos en la evaluación, revise!!')]






    # @api.onchange('curso_id')
    # def get_aspecto_evaluarc(self):
    #     for model in self:
    #          self.aspecto_evaluar_id = False
    #
    #          if model.curso_id:
    #              return {'domain': {'aspecto_evaluar_id': [('id', 'in', model.curso_id.aspecto_ids.ids)]}}

    # @api.onchange('empleado_id')
    # def get_aspecto_evaluar(self):
    #      self.aspecto_evaluar_id = False
    #
    #      if self.empleado_id:
    #          return {'domain': {'aspecto_evaluar_id': [('id', 'in', self.empleado_id.curso.aspecto_ids.ids)]}}


class Estudiante(models.Model):
    _name = 'app_seleccion.estudiante'

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

    name = fields.Char(string='Nombre',size=60, required=True)
    ci = fields.Char(string='Carnet de Identidad', size=11, required=True)
    #campos para gestionar los cursos
    curso = fields.Many2one('app_seleccion.curso',string='Curso', required=True)
    fecha_inicio = fields.Date('Fecha de inicio')
    fecha_fin = fields.Date('Fecha de fin')
    horas = fields.Integer('Cantidad de horas')
    nombre_curso = fields.Char('Nombre Curso',related='curso.name',Store=True)
    active = fields.Boolean('Activo',default=True)
    mes_curso = fields.Char('Mes del Curso',compute='_get_mes_curso',store=True)
    @api.depends('fecha_inicio')
    def _get_mes_curso(self):
        if self.fecha_inicio:
            mes = self.fecha_inicio
            mes = mes.split('-')
            self.mes_curso = mes[1]

    mes_curso_nombre = fields.Char('Mes del curso',compute='_get_mes_curso_nombre',store=True)
    @api.depends('fecha_inicio')
    def _get_mes_curso_nombre(self):
        if self.fecha_inicio:
            mes = self.fecha_inicio
            mes = mes.split('-')
            self.mes_curso_nombre = self.get_nombre_mes(mes[1])

    year_curso = fields.Char('Año del Curso',compute='_get_year_curso',store=True)
    @api.depends('fecha_inicio')
    def _get_year_curso(self):
        if self.fecha_inicio:
            year = self.fecha_inicio
            year = year.split('-')
            self.year_curso = year[0]

    evaluacion_id = fields.One2many(comodel_name='app_seleccion.evaluacion',inverse_name='estudiante_id',string='Evaluación')
    valoracion_cualitativa = fields.Text(string='Valoración Cualitativa')
    evaluacion_final = fields.Integer(string='Evaluación Final',size=3,readonly=True,compute='_get_evaluacion_final',store=True)


    @api.depends('evaluacion_id')
    @api.one
    def _get_evaluacion_final(self):
        sum = 0
        count = 0
        for element in self.evaluacion_id:
            sum = sum + element.evaluacion
            count = count + 1
        if count > 0:
            self.evaluacion_final = sum/count
        else:
            return 0

    evaluado = fields.Boolean('Evaluado',compute='_get_evaluated',store=True)

    @api.depends('evaluacion_final')
    @api.one
    def _get_evaluated(self):
        if self.evaluacion_final > 0:
            self.evaluado = True
        else:
            self.evaluado = False


    #validar que se introduzca el curso
    @api.constrains('curso')
    def _check_curso(self):
        if not self.curso:
            raise ValidationError(_("Debe escoger el Curso de Habilitacion!!"))

    #validar que se introduzca el nombre del estudiante
    @api.constrains('name')
    def _check_name(self):
        if not self.name:
            raise ValidationError(_("Debe escribir el nombre del estudiante!!"))

    # validar que la fecha inicio sea menor que la de fin
    @api.constrains('fecha_inicio', 'fecha_fin')
    def _check_fechas(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio > self.fecha_fin:
            raise ValidationError(_("La fecha de inicio no puede ser mayor que la de fin !!"))


    @api.multi
    def imprimir_registro_evaluacion(self):
        if not self.curso:
            raise ValidationError(_("Debe asignarle un curso al estudiante y evaluar cada uno de los aspectos del curso !!"))
        elif not self.horas:
            raise ValidationError(_("Debe introducir la cantidad de horas del curso !!"))
        elif not self.fecha_inicio:
            raise ValidationError(_("Debe introducir la fecha de inicio del curso !!"))
        elif not self.fecha_fin:
            raise ValidationError(_("Debe introducir la fecha de fin del curso !!"))

        datas = {}

        lista_evaluaciones = []

        contador = 0
        for elemento in self.evaluacion_id:
            evaluacion = {}
            contador = contador + 1
            evaluacion['numero'] = str(contador)
            #buscar el nombre de este aspecto
            aspect = self.env['app_seleccion.aspecto'].search([('id','=',elemento.aspecto_evaluar_id.id)])
            evaluacion['aspecto_evaluar_name'] = aspect.name

            #si tiene al menos un aspecto sin evaluar no se imprime registro evaluacion
            if elemento.evaluacion == '0':
                 raise ValidationError(_("Tiene aspectos sin evaluar, debe completarlos antes de imprimir el Registro de evaluación !!"))

            evaluacion['evaluacion'] = elemento.evaluacion
            lista_evaluaciones.append(evaluacion)


        fecha_hoy = fields.Date.today()
        datas['fecha'] = fecha_hoy
        datas['ci'] = self.ci
        datas['nombre_curso'] = self.nombre_curso
        datas['lista_evaluaciones'] = lista_evaluaciones
        datas['nombre_estudiante'] = self.name
        datas['f_inicio'] = self.fecha_inicio
        datas['f_fin'] = self.fecha_fin
        datas['horas'] = self.horas
        datas['evaluacion_final'] = self.evaluacion_final


        if self.valoracion_cualitativa != False:
            datas['valoracion_cualitativa'] = self.valoracion_cualitativa
        else:
            datas['valoracion_cualitativa'] = 'No posee'


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_revaluacion_report',
                    'datas': datas,
                }





