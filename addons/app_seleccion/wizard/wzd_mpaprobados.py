# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Mpaprobados(models.TransientModel):
    _name = 'app_seleccion.wzd_mpaprobados'

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

    def get_year(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])

        lista = []
        for i in range(2004,year+1):
            year_reg = (i,i)
            lista.append(year_reg)
        return lista

    year = fields.Selection(selection='get_year',String='Año')

    def get_year_revolution(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])
        year_revolution = year - 1959
        return year_revolution


    #validar que se introduzca el curso
    @api.constrains('year')
    def _check_year(self):
        if not self.year:
            raise ValidationError(_("Debe escoger el año !!"))
        else:
            count = self.env['hr.applicant'].search_count(['&',('year', '=', self.year),'|','|',('estado', '=', 'aprobado'),('estado', '=', 'reserva'),('estado', '=', 'curso')])
            if count == 0:
                raise ValidationError(_("No existen candidatos aprobados para ese año !!"))


    @api.multi
    def imprimir(self):

        candidatos = self.env['hr.applicant'].search(['&',('year', '=', self.year),'|','|',('estado', '=', 'aprobado'),('estado', '=', 'reserva'),('estado', '=', 'curso')])
        datas = {}
        lista_candidatos = []
        contador = 0

        for c in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['num'] = contador
            candidato['ci'] = c.ci
            candidato['nombre'] = c.partner_name
            candidato['nivel'] = c.school_level_id.name
            candidato['calificacion'] = c.degree_id.name
            if c.estado == 'aprobado':
                candidato['estado'] = c.nombre_trabajo
            elif c.estado == 'curso':
                candidato['estado'] = c.nombre_curso
            else:
                candidato['estado'] = 'Reserva'
            lista_candidatos.append(candidato)



        datas['lista_candidatos'] = lista_candidatos
        fecha_hoy = fields.Date.today()
        fecha_hoy = fecha_hoy.split('-')
        datas['year_hoy'] = fecha_hoy[0]
        datas['mes_hoy'] = self.get_nombre_mes(fecha_hoy[1])
        datas['dia_hoy'] = fecha_hoy[2]
        datas['year_revolution'] = self.get_year_revolution()
        datas['year'] = self.year
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mpaprobados_report',
                    'datas': datas,
                }
