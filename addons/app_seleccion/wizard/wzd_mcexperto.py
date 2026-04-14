# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Cexperto(models.TransientModel):
    _name = 'app_seleccion.wzd_mcexperto'

    def get_year_revolution(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])
        year_revolution = year - 1959
        return year_revolution

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


    #validar que se introduzca el mes y el año
    @api.constrains('mes','year')
    def _check_params(self):
         if not self.mes:
             raise ValidationError(_("Debe escoger el mes !!"))
         elif not self.year:
             raise ValidationError(_("Debe escoger el año !!"))
         else:
             sql_expertos_total = "SELECT count(hr_applicant.name) FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
             self.env.cr.execute(sql_expertos_total,(self.mes,self.year))
             total_expertos = self.env.cr.fetchone()


             if total_expertos[0] == 0:
               raise ValidationError(_("No existen candidatos en Comité de Expertos para ese mes y año !!"))

    @api.multi
    def imprimir(self):
        datas = {}
        fecha_hoy = fields.Date.today()
        datas['fecha'] = fecha_hoy
        fecha_hoy = fecha_hoy.split('-')
        year = fecha_hoy[0]
        mes = self.get_nombre_mes(fecha_hoy[1])
        dia = fecha_hoy[2]

        sql_expertos_total = "SELECT hr_applicant.name,hr_applicant.ci,hr_applicant.nombre_trabajo,hr_applicant.nombre_curso,app_seleccion_solicitud_expertos.tiempo_en_comite,app_seleccion_solicitud_expertos.fecha_solicitud,app_seleccion_solicitud_expertos.fecha_fin FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total,(self.mes,self.year))
        candidatos = self.env.cr.fetchall()


        lista_candidatos = []
        contador = 0
        for elemento in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['numero'] = str(contador)
            candidato['nombre'] = elemento[0]
            candidato['ci'] = elemento[1]
            candidato['trabajo'] = elemento[2]
            candidato['curso'] = elemento[3]
            candidato['tiempo'] = elemento[4]
            candidato['fecha_s'] = elemento[5]
            candidato['fecha_fin'] = elemento[6]
            lista_candidatos.append(candidato)

        datas['lista_candidatos'] = lista_candidatos
        datas['year'] = year
        datas['mes'] = mes
        datas['yearc'] = self.year
        datas['mesc'] = self.get_nombre_mes(self.mes)
        datas['year_revolution'] = self.get_year_revolution()
        datas['dia'] = dia


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mcexperto_report',
                    'datas': datas,
                }




