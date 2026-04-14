# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Rechazada(models.TransientModel):
    _name = 'app_seleccion.wzd_msrechazada'

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

    #validar que se introduzca el año
    @api.constrains('year')
    def _check_year(self):
        if not self.year :
            raise ValidationError(_("Debe introducir el año!!"))
        else:
            count = self.env['hr.applicant'].search_count([('estado', '=', 'rechazado'),('year', '=', self.year)])
            if count == 0:
                raise ValidationError(_("No existen solicitudes rechazadas para ese año!!"))

    
    @api.multi
    def imprimir(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = year[0]
        candidatos = self.env['hr.applicant'].search([('estado', '=', 'rechazado'),('year', '=', self.year)])

        datas = {}
        lista_candidatos = []
        contador = 0
        for elemento in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['numero'] = str(contador)
            candidato['nombre'] = elemento.partner_name
            candidato['ci'] = elemento.ci

            if not elemento.nombre_curso:
                candidato['trabajo'] = elemento.nombre_trabajo
            else:
                candidato['trabajo'] = elemento.nombre_curso

            lista_candidatos.append(candidato)

        datas['lista_candidatos'] = lista_candidatos
        datas['year'] = self.year
        datas['fecha'] = fields.Date.today()


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_msrechazada_report',
                    'datas': datas,
                }
