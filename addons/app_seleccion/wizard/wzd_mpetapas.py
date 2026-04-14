# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Mpetapas(models.TransientModel):
    _name = 'app_seleccion.wzd_mpetapas'

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

        

    stage_id = fields.Many2one('hr.recruitment.stage', string='Etapa',track_visibility='onchange')

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


    #validar que se introduzca la etapa
    @api.constrains('stage_id','mes','year')
    def _check_stage(self):
        if not self.stage_id:
            raise ValidationError(_("Debe escoger la etapa !!"))
        elif not self.mes:
            raise ValidationError(_("Debe escoger el mes !!"))
        elif not self.year:
            raise ValidationError(_("Debe escoger el año !!"))
        else:
            count = self.env['hr.applicant'].search_count([('stage_id', '=', self.stage_id.id),('estado', '=', 'proceso'),('mes','=',self.mes),('year','=',self.year)])
            if count == 0:
                raise ValidationError(_("No existen candidatos activos para esa etapa !!"))


    @api.multi
    def imprimir(self):

        candidatos = self.env['hr.applicant'].search([('stage_id', '=', self.stage_id.id),('estado', '=', 'proceso'),('mes','=',self.mes),('year','=',self.year)])
        datas = {}
        lista_candidatos = []
        contador = 0

        for c in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['num'] = contador
            candidato['ci'] = c.ci
            candidato['nombre'] = c.partner_name
            candidato['puesto_trabajo'] = c.nombre_trabajo
            candidato['curso'] = c.nombre_curso
            lista_candidatos.append(candidato)



        datas['lista_candidatos'] = lista_candidatos
        fecha_hoy = fields.Date.today()
        fecha_hoy = fecha_hoy.split('-')
        datas['year_hoy'] = fecha_hoy[0]
        datas['mes_hoy'] = self.get_nombre_mes(fecha_hoy[1])
        datas['dia_hoy'] = fecha_hoy[2]
        datas['year_revolution'] = self.get_year_revolution()
        datas['etapa'] = self.stage_id.name
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_metapas_report',
                    'datas': datas,
                }
