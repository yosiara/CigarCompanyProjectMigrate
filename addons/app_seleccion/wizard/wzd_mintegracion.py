# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Integracion(models.TransientModel):
    _name = 'app_seleccion.wzd_mintegracion'


    numero = fields.Many2one('app_seleccion.solicitud_expertos', string='Numero de Solicitud',track_visibility='onchange')


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


    #validar que se introduzca el puesto de trabajo y que existan solicitudes para ese puesto
    @api.constrains('numero','year')
    def _check_numero(self):
         if not self.numero :
             raise ValidationError(_("Debe escoger el numero de Solicitud !!"))
         elif not self.year:
             raise ValidationError(_("Debe escoger el año !!"))
         else:
             sql_expertos_total = "SELECT count(hr_applicant.name) FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.numero_solicitud = %s and app_seleccion_solicitud_expertos.year = %s"
             self.env.cr.execute(sql_expertos_total,(self.numero.numero_solicitud,self.year))
             total_expertos = self.env.cr.fetchone()

             #de fuente interna
             sql_expertos_total_internos = "SELECT count(hr_employee.name_related) FROM (hr_employee INNER JOIN app_seleccion_solicitud_expertos_hr_employee_rel ON" \
                             " hr_employee.id = app_seleccion_solicitud_expertos_hr_employee_rel.hr_employee_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_employee_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.numero_solicitud = %s and app_seleccion_solicitud_expertos.year = %s"
             self.env.cr.execute(sql_expertos_total_internos,(self.numero.numero_solicitud,self.year))
             total_expertos_internos = self.env.cr.fetchone()


             if total_expertos[0] + total_expertos_internos[0] == 0:
               raise ValidationError(_("No existen solicitudes en Comité de Expertos para ese Puesto de Trabajo !!"))

    @api.multi
    def imprimir(self):
        datas = {}
        fecha_hoy = fields.Date.today()
        datas['fecha'] = fecha_hoy
        fecha_hoy = fecha_hoy.split('-')
        year = fecha_hoy[0]
        mes = self.get_nombre_mes(fecha_hoy[1])
        dia = fecha_hoy[2]

        sql_expertos_total = "SELECT hr_applicant.name,hr_applicant.ci,hr_applicant.nombre_trabajo,hr_applicant.nombre_curso FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.numero_solicitud = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total,(self.numero.numero_solicitud,self.year))
        candidatos = self.env.cr.fetchall()

        #de fuente interna
        sql_expertos_total_internos = "SELECT hr_employee.name_related FROM (hr_employee INNER JOIN app_seleccion_solicitud_expertos_hr_employee_rel ON" \
                             " hr_employee.id = app_seleccion_solicitud_expertos_hr_employee_rel.hr_employee_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_employee_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.numero_solicitud = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total_internos,(self.numero.numero_solicitud,self.year))
        expertos_internos = self.env.cr.fetchall()




        lista_candidatos = []
        contador = 0
        for elemento in candidatos:
            candidato = {}
            contador = contador + 1
            candidato['numero'] = str(contador)
            candidato['nombre'] = elemento[0]

            lista_candidatos.append(candidato)

        for elemento in expertos_internos:
            candidato = {}
            contador = contador + 1
            candidato['numero'] = str(contador)
            candidato['nombre'] = elemento[0]


            lista_candidatos.append(candidato)

        datas['lista_candidatos'] = lista_candidatos
        datas['puesto_trabajo'] = self.numero.job_id.name
        datas['year'] = year
        datas['mes'] = mes
        datas['dia'] = dia


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mintegracion_report',
                    'datas': datas,
                }




