# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Mecurso(models.TransientModel):
    _name = 'app_seleccion.wzd_mecurso'

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

        

    curso_id = fields.Many2one('app_seleccion.curso',track_visibility='onchange')

    def get_mes(self):
        lista = []
        enero = ('01','enero')
        febrero = ('02','febrero')
        marzo = ('03','marzo')
        abril = ('04','abril')
        mayo = ('05','mayo')
        junio = ('06','junio')
        julio = ('07','julio')
        agosto = ('08','agosto')
        septiembre = ('09','septiembre')
        octubre = ('10','octubre')
        noviembre = ('11','noviembre')
        diciembre = ('12','diciembre')

        lista.append(enero)
        lista.append(febrero)
        lista.append(marzo)
        lista.append(abril)
        lista.append(mayo)
        lista.append(junio)
        lista.append(julio)
        lista.append(agosto)
        lista.append(septiembre)
        lista.append(octubre)
        lista.append(noviembre)
        lista.append(diciembre)

        return lista

    mes = fields.Selection(selection='get_mes')

    def get_year(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])

        lista = []
        for i in range(2004,year+1):
            year_reg = (i,i)
            lista.append(year_reg)
        return lista

    year = fields.Selection(selection='get_year')

    def get_year_revolution(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])
        year_revolution = year - 1959
        return year_revolution


    #validar que se introduzca el curso
    @api.constrains('curso_id')
    def _check_curso(self):
        if not self.curso_id:
            raise ValidationError(_("Debe escoger el curso !!"))
        else:
            count = self.env['app_seleccion.estudiante'].search_count([('curso', '=', self.curso_id.id),('mes_curso','=',self.mes),
                                                                       ('year_curso','=',self.year)])
            if count == 0:
                raise ValidationError(_("No existen estudiantes registrados para ese curso !!"))


    @api.multi
    def imprimir(self):

        estudiantes = self.env['app_seleccion.estudiante'].search([('curso', '=', self.curso_id.id),('mes_curso','=',self.mes),
                                                                       ('year_curso','=',self.year)])
        datas = {}
        lista_estudiantes = []
        contador = 0

        for c in estudiantes:
            estudiante = {}
            contador = contador + 1
            estudiante['num'] = contador
            estudiante['ci'] = c.ci
            estudiante['nombre'] = c.name
            estudiante['evaluacion'] = c.evaluacion_final
            estudiante['valoracion'] = c.valoracion_cualitativa
            lista_estudiantes.append(estudiante)

        datas['lista_estudiantes'] = lista_estudiantes
        fecha_hoy = fields.Date.today()
        fecha_hoy = fecha_hoy.split('-')
        datas['year_hoy'] = fecha_hoy[0]
        datas['mes_hoy'] = self.get_nombre_mes(fecha_hoy[1])
        datas['dia_hoy'] = fecha_hoy[2]
        datas['year_revolution'] = self.get_year_revolution()
        datas['curso'] = self.curso_id.name
        datas['year'] = self.year
        datas['mes'] = self.get_nombre_mes(self.mes)
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mecurso_report',
                    'datas': datas,
                }
