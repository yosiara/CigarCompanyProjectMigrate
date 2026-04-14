# -*- coding: utf-8 -*-

from odoo import tools, osv
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from pytz import timezone
from dateutil.relativedelta import relativedelta

import logging
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class l10n_cu_hlg_hr_import_attendance_import_wzd(models.TransientModel):
    _name = "l10n_cu_hlg_hr_import.attendance_import_wzd"

    def get_previous_date(self):
        previous_date = fields.Date.from_string(fields.Date.today())
        previous_date -= relativedelta(days=35)
        return previous_date

    fecha_inicio = fields.Date('Fecha inicio', required=True, default=get_previous_date)
    fecha_fin = fields.Date('Fecha Fin', required=True, default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', 'Employee', copy=False)
    connector_id = fields.Many2one('db_external_connector.template', 'Database', required=True)

    def get_reason_type(self, conn):
        """ Get reasons type from fastos"""
        cursor = conn.cursor()
        cursor.execute("""
        SELECT Id_TipoClaveAsistencia,NombreTipoClaveAsistencia
          FROM CPT_TiposClavesAsistencia""")
        res = []
        for row in cursor.fetchall():
            res.append((row[0], row[1]))
        return res

    def do_import_reason_type(self, conn=None):
        disconnect = False
        if not conn:
            conn = self.connector_id.connect()
            disconnect = True
        type_obj = self.env['hr_turei.attendance_reason_type']

        for type_code, type_name in self.get_reason_type(conn):
            type_ids = type_obj.search([('code', '=', tools.ustr(type_code))])
            if not type_ids:
                type_obj.create({
                    'name': tools.ustr(type_name),
                    'code': tools.ustr(type_code),
                })
                _logger.info(_("Type created: %s"), type_name)
        if disconnect:
            conn.close()

    def get_reason(self, conn):
        """ Get reasons from fastos"""
        cursor = conn.cursor()
        cursor.execute("""
        SELECT Id_ClaveAsistencia,NombreClaveAsistencia,Id_TipoClaveAsistencia
      FROM CPT_ClavesAsistencia""")
        res = []
        for row in cursor.fetchall():
            res.append((row[0], row[1], row[2]))
        return res

    def do_import_reason(self, conn=None):
        _logger.info("Importando Claves de asistencia....")
        disconnect = False
        if not conn:
            conn = self._context.get('connector_id').connect()
        type_obj = self.env['hr_turei.attendance_reason_type']
        reason_obj = self.env['hr_turei.attendance_reason']
        cursor = conn.cursor()
        cursor.execute("""
                SELECT Id_ClaveAsistencia,NombreClaveAsistencia,Id_TipoClaveAsistencia
              FROM CPT_ClavesAsistencia""")

        for row in cursor:
            # Busco por el codigo del tipo de la clave de asistencia
            type_ids = type_obj.search([('code', '=', tools.ustr(row[2]))])
            # Busco por el codigo de la clave de asistencia
            reason_ids = reason_obj.search([('code', '=', tools.ustr(row[0]))])
            # Si no está la clave de asistencia se crea
            if not reason_ids and type_ids:
                reason_obj.create({
                    'name': tools.ustr(row[1]),
                    'code': tools.ustr(row[0]),
                    'type': tools.ustr(type_ids[0].id),
                }, )
                _logger.info("Clave de asistencia creada: %s", tools.ustr(row[1]))
        if disconnect:
            conn.close()

    def get_empl_ids(self, conn):
        cursor = conn.cursor()
        employee_code = self.employee_id.external_id if self.employee_id else False
        query = ''
        if employee_code:
            query = """select CPT_Empleados.Id_Empleado from  CPT_Empleados Where Id_Empleado='%s';""" % (employee_code)
        else:
            query = """select CPT_Empleados.Id_Empleado from  CPT_Empleados"""
        cursor.execute(query)
        res = []
        for row in cursor.fetchall():
            att = {}
            att['id_Empleado'] = row[0]
            res.append(att)
        return res

    def get_empl_clasifica_fecha(self, conn, id_empleado, fecha):
        _logger.info("Obteniendo clasificacion por fecha")
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT id_ClaveAsistencia, Turno, CantidadHoras 
                      FROM dbo.CPT_ClasificacionAsistencia
                      where [Id_Empleado] = '""" + str(id_empleado) + """' and [Fecha] = '""" + str(fecha) + """' 
        """)
        res = []
        for row in cursor.fetchall():
            att = {}
            att['id_ClaveAsistencia'] = row[0]
            att['Turno'] = row[1]
            att['CantidadHoras'] = row[2]
            res.append(att)
        return res

    def do_import_attendances(self, conn=None):
        _logger.info("Comenzando a importar asistencias en la fecha establecida")

        connection = self.connector_id.connect()
        self.do_import_reason_type(connection)
        self.do_import_reason(connection)
        conn = connection
        disconnect = True

        emp_obj = self.env['hr.employee']
        incidence_obj = self.env['hr_turei.attendance_incidence']
        reason_obj = self.env['hr_turei.attendance_reason']

        fecha_min = False
        true_inc_ids = []
        temp_fecha_min = datetime.strptime(self.fecha_inicio, DEFAULT_SERVER_DATE_FORMAT)
        temp_fecha_max = datetime.strptime(self.fecha_fin, DEFAULT_SERVER_DATE_FORMAT)
        empleados_id = self.get_empl_ids(conn)
        for emp_id in empleados_id:
            fecha = temp_fecha_min
            un_dia = timedelta(days=1)
            while fecha <= temp_fecha_max:

                emp_ids = emp_obj.search([('external_id', '=', emp_id['id_Empleado'])])
                fecha_str = datetime.strftime(fecha, DEFAULT_SERVER_DATE_FORMAT)

                # Buscar incidencias
                result = self.get_empl_clasifica_fecha(conn, emp_id['id_Empleado'], fecha)
                for incidence in result:
                    # si existe el empleado entonces busco las incidencias
                    if emp_ids:
                        incidence_ids = incidence_obj.search([('employee_id', '=', emp_ids[0].id),
                                                              ('date', '=', fecha),
                                                              ('employee_turn', '=', incidence['Turno']),
                                                              ('employee_turn_order', '=', 1)], )
                        # SINO ESTA LA INCIDENCIA SE CREA UNA NUEVA
                        if not incidence_ids:
                            dict_campos = {
                                'employee_id': emp_ids[0].id,
                                'company_id': emp_ids[0].company_id.id,
                                'date': fecha,
                                'employee_turn': incidence['Turno'],
                                'employee_turn_order': 1,
                                'entry_date': False,
                                'exit_date': False,
                                'working_time': 0,
                                'not_working_time': incidence['CantidadHoras'],
                            }

                            reason_ids = reason_obj.search([('code', '=', incidence['id_ClaveAsistencia'])])
                            if len(reason_ids) > 0:
                                dict_campos['reason_id'] = reason_ids[0].id
                            incidence_item = incidence_obj.create(dict_campos)
                            true_inc_ids.append(incidence_item.id)
                            _logger.info("Incidencia creada: %s", fecha)
                        else:
                            true_inc_ids.append(incidence_ids[0].id)
                            # SI ESTA EN LA INTRANET Y ESTA CLASIFICADA EN EL FASTOS SE ACTUALIZA CON LA CLASIFICACION QUE TIENE EN EL FASTOS
                            reason_ids = reason_obj.search([('code', '=', incidence['id_ClaveAsistencia'])])
                            dict_campos_act = {
                                'company_id': emp_ids[0].company_id.id,
                                'working_time': 0,
                                'not_working_time': incidence['CantidadHoras'],
                            }

                            if len(reason_ids) > 0:
                                dict_campos_act['reason_id'] = reason_ids[0].id
                                incidence_ids.write(dict_campos_act)
                                _logger.info("Actualizando clasificada: %s", fecha)
                    else:
                        print emp_id['id_Empleado']

                fecha += un_dia
        self._cr.commit()

        if self.employee_id:
            incidence_ids = incidence_obj.search(
                [('date', '>=', fecha_min), ('date', '<=', temp_fecha_max), ('id', 'not in', true_inc_ids),
                 ('employee_id', '=', self.employee_id.id)])
            incidence_ids.unlink()
        else:
            incidence_ids = incidence_obj.search(
                [('date', '>=', fecha_min), ('date', '<=', temp_fecha_max), ('id', 'not in', true_inc_ids)])
            incidence_ids.unlink()
        self._cr.commit()
        if disconnect:
            conn.close()
        # si llega hasta este punto todoesta bien
        return True
