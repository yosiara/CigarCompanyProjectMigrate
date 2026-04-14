# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Mpcurso(models.TransientModel):
    _name = 'app_seleccion.wzd_mpcurso'

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
            count = self.env['hr.applicant'].search_count([('curso_habilitacion', '=', self.curso_id.id),('estado', '=', 'proceso')])
            if count == 0:
                raise ValidationError(_("No existen candidatos activos para ese curso !!"))


    @api.multi
    def imprimir(self):

        candidatos = self.env['hr.applicant'].search([('curso_habilitacion', '=', self.curso_id.id),('estado', '=', 'proceso')])
        datas = {}
        lista_candidatos = []
        contador = 0

        for c in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['num'] = contador
            candidato['ci'] = c.ci
            candidato['nombre'] = c.partner_name
            candidato['calificacion'] = c.degree_id.name
            lista_candidatos.append(candidato)



        datas['lista_candidatos'] = lista_candidatos
        fecha_hoy = fields.Date.today()
        fecha_hoy = fecha_hoy.split('-')
        datas['year_hoy'] = fecha_hoy[0]
        datas['mes_hoy'] = self.get_nombre_mes(fecha_hoy[1])
        datas['dia_hoy'] = fecha_hoy[2]
        datas['year_revolution'] = self.get_year_revolution()
        datas['curso'] = self.curso_id.name
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mpcurso_report',
                    'datas': datas,
                }
