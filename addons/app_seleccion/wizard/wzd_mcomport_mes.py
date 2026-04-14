# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class ComportamientoMes(models.TransientModel):
    _name = 'app_seleccion.wzd_comport_mes'

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


    #validar que se introduzca el año y el mes
    @api.constrains('year','mes')
    def _check_year_mes(self):
        if not self.year:
            raise ValidationError(_("Debe introducir el año !!"))
        elif not self.mes:
            raise ValidationError(_("Debe introducir el mes !!"))
        else:
            count = self.env['hr.applicant'].search_count([('mes', '=', self.mes),('year', '=', self.year)])
            if count == 0:
                raise ValidationError(_("No existen solicitudes realizadas durante el mes seleccionado !!"))


    
    @api.multi
    def imprimir(self):

        candidatos = self.env['hr.applicant'].search([('mes', '=', self.mes),('year', '=', self.year)])
        total_candidatos = self.env['hr.applicant'].search_count([('mes', '=', self.mes),('year', '=', self.year)])


        datas = {}
        lista_puestos = []
        lista_puestos_expertos = []


        sql = "select nombre_trabajo,count(nombre_trabajo) from hr_applicant where hr_applicant.mes = %s " \
              "and hr_applicant.year=%s and hr_applicant.nombre_trabajo IS NOT NULL group by nombre_trabajo"

        self.env.cr.execute(sql,(self.mes,int(self.year)))
        candidatos_puestos = self.env.cr.fetchall()
        for c in candidatos_puestos:
            puesto = {}
            puesto['cantidad'] = c[1]
            puesto['puesto_trabajo'] = c[0]
            lista_puestos.append(puesto)

        #candidatos por cursos
        sql_cursos = "select nombre_curso,count(nombre_curso) from hr_applicant where hr_applicant.mes = %s and hr_applicant.year=%s and hr_applicant.nombre_curso IS NOT NULL and hr_applicant.nombre_trabajo is NULL group by nombre_curso"
        self.env.cr.execute(sql_cursos,(self.mes,int(self.year)))
        candidatos_cursos = self.env.cr.fetchall()
        for c in candidatos_cursos:
            puesto = {}
            puesto['cantidad'] = c[1]
            puesto['puesto_trabajo'] = c[0]
            lista_puestos.append(puesto)

        sql_expertos = "SELECT hr_applicant.nombre_trabajo,count(hr_applicant.nombre_trabajo) FROM " \
                       "(hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                       "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                       "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s and app_seleccion_solicitud_expertos.curso_id IS NULL  group by hr_applicant.nombre_trabajo"
        self.env.cr.execute(sql_expertos,(self.mes,self.year))
        candidatos_expertos = self.env.cr.fetchall()
        for c in candidatos_expertos:
            puesto = {}
            puesto['cantidad'] = c[1]
            puesto['puesto_trabajo'] = c[0]
            lista_puestos_expertos.append(puesto)

        #comite de expertos por cursos
        sql_expertos_cursos = "SELECT hr_applicant.nombre_curso,count(hr_applicant.nombre_curso) FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel " \
                              "ON hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) INNER JOIN app_seleccion_solicitud_expertos " \
                              "ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                              "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s and hr_applicant.nombre_curso " \
                              "IS NOT NULL and app_seleccion_solicitud_expertos.job_id IS NULL group by hr_applicant.nombre_curso"
        self.env.cr.execute(sql_expertos_cursos,(self.mes,self.year))
        candidatos_expertos_cursos = self.env.cr.fetchall()
        for c in candidatos_expertos_cursos:
            puesto = {}
            puesto['cantidad'] = c[1]
            puesto['puesto_trabajo'] = c[0]
            lista_puestos_expertos.append(puesto)

        #de fuente externa
        sql_expertos_total = "SELECT count(hr_applicant.name) FROM (hr_applicant INNER JOIN app_seleccion_solicitud_expertos_hr_applicant_rel ON" \
                             " hr_applicant.id = app_seleccion_solicitud_expertos_hr_applicant_rel.hr_applicant_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_applicant_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total,(self.mes,self.year))
        total_expertos = self.env.cr.fetchone()

        #de fuente interna
        sql_expertos_total_internos = "SELECT count(hr_employee.name_related) FROM (hr_employee INNER JOIN app_seleccion_solicitud_expertos_hr_employee_rel ON" \
                             " hr_employee.id = app_seleccion_solicitud_expertos_hr_employee_rel.hr_employee_id) " \
                             "INNER JOIN app_seleccion_solicitud_expertos ON app_seleccion_solicitud_expertos_hr_employee_rel.app_seleccion_solicitud_expertos_id = app_seleccion_solicitud_expertos.id " \
                             "and app_seleccion_solicitud_expertos.mes_experto = %s and app_seleccion_solicitud_expertos.year = %s"
        self.env.cr.execute(sql_expertos_total_internos,(self.mes,self.year))
        total_expertos_internos = self.env.cr.fetchone()


        datas['lista_puestos'] = lista_puestos
        datas['lista_puestos_expertos'] = lista_puestos_expertos
        datas['year'] = self.year
        datas['mes'] = self.get_nombre_mes(self.mes)
        fecha_hoy = fields.Date.today()
        fecha_hoy = fecha_hoy.split('-')
        datas['year_hoy'] = fecha_hoy[0]
        datas['mes_hoy'] = self.get_nombre_mes(fecha_hoy[1])
        datas['dia_hoy'] = fecha_hoy[2]
        datas['total_candidatos'] = total_candidatos
        datas['total_expertos'] = total_expertos[0] + total_expertos_internos[0]
        datas['year_revolution'] = self.get_year_revolution()
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_mcomport_mes_report',
                    'datas': datas,
                }
