# -*- coding: utf-8 -*-
import logging
from datetime import datetime, date

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger('INFO')


class ImportEmployeeWizard(models.TransientModel):
    _name = "l10n_cu_hr_import.import_employee_wizard"

    def _get_default_connector(self):
        return self.env['db_external_connector.template'].search(
            [('application', '=', 'fastos')], limit=1
        ).id or False

    connector_id = fields.Many2one(
        'db_external_connector.template',  'Database',  required=True, default=_get_default_connector
    )

    def get_company(self, id_area):
        if id_area in ['01', '011', '11', '12']:
            company = self.env['res.company'].search([('code', '=', '001')], limit=1)
            return company.id if company else False
        if id_area in ['02', '03', '04', '05', '051']:
            company = self.env['res.company'].search([('code', '=', '002')], limit=1)
            return company.id if company else False
        if id_area == '06':
            company = self.env['res.company'].search([('code', '=', '003')], limit=1)
            return company.id if company else False
        if id_area in ['07', '08', '09']:
            company = self.env['res.company'].search([('code', '=', '004')], limit=1)
            return company.id if company else False
        if id_area in ['10']:
            company = self.env['res.company'].search([('code', '=', '005')], limit=1)
            return company.id if company else False
        if id_area == '13':
            company = self.env['res.company'].search([('code', '=', '006')], limit=1)
            return company.id if company else False

    @api.one
    def action_import(self):
        self.action_import_function()
        return True

    @api.model
    def action_import_function(self):
        obj = self
        if self._context.get('connector_id'):
            connection = self._context.get('connector_id').connect()
            obj = self.create({'connector_id': self._context.get('connector_id').id})
        else:
            connection = self.connector_id.connect()

        obj.import_employees(connection)
        # obj.import_employees_schedule(connection)
        connection.close()
        return True

    @api.one
    def import_employees(self, connection):
        # Updating departments...
        self.import_departments(connection)
        department_obj = self.env['hr.department']
        departments = department_obj.search([])

        departments_dict = {}
        for department in departments:
            departments_dict[department.external_id] = department.id

        # Updating jobs...
        self.import_employee_jobs(connection)
        job_obj = self.env['hr.job']
        jobs = job_obj.search([])

        jobs_dict = {}
        for job in jobs:
            jobs_dict[job.external_id] = job.id

        # Updating defence location....
        self.import_employee_defence_location(connection)
        defence_location_obj = self.env['l10n_cu_hlg_hr.employee_defence_location_type']
        defence_locations = defence_location_obj.search([])

        defence_locations_dict = {}
        for defence_location in defence_locations:
            defence_locations_dict[defence_location.external_id] = defence_location.id

        # Updating employee's school level...
        self.import_employee_school_level(connection)
        school_level_obj = self.env['l10n_cu_hlg_hr.employee_school_level']
        school_levels = school_level_obj.search([])

        school_levels_dict = {}
        for school_level in school_levels:
            school_levels_dict[school_level.external_id] = school_level.id

        # Updating employee directory..
        cursor = connection.cursor()

        try:
            cursor.execute("""Select Id_Empleado, CI, Nombre + ' ' + PrimerApellido + ' ' + SegundoApellido AS nombre,
                                     Sexo, Id_Cargo, Id_Departamento, Id_Area, Telefono, Id_Raza, Id_EstadoCivil,
                                     FechaNacimiento, CPT_IntegracionPolitica.NombreIntegracionPolitica, NacidoEn,
                                     FechaAltaActividad, Id_Ubicacion, SituacionDefensa, Id_Nivel, Direccion, NombreProvincia, NombreMunicipio
                              FROM CPT_Empleados 
                              LEFT JOIN CGT_Municipios ON CPT_Empleados.Id_Municipio = CGT_Municipios.Id_Municipio AND CPT_Empleados.Id_Provincia = CGT_Municipios.Id_Provincia 
                              LEFT JOIN CGT_Provincias ON CPT_Empleados.Id_Provincia = CGT_Provincias.Id_Provincia 
                              LEFT JOIN CPT_IntegracionPolitica ON CPT_IntegracionPolitica.Id_IntegracionPolitica = CPT_Empleados.Id_IntegracionPolitica;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        country_obj = self.env['res.country']
        country = country_obj.search([('code', '=', 'CU')],limit=1)

        race = {'N': 'black', 'B': 'white', 'M': 'mixed', 'A': 'black'}
        marital_status = {'S': 'single', 'C': 'married', 'V': 'widower', 'D': 'divorced'}
        political_affiliations = {'PCC': 'pcc', 'UJC': 'ujc', 'PCC y UJC': 'both', 'No Militante': 'none'}

        employee_obj = self.env['hr.employee']
        employee_obj.search([]).with_context(no_create_movement=True).write({'active': False})
        for row in cursor:
            if row[11] == None:
                afili = 'No Militante'
            else:
                afili = row[11]

            employee_data = {
                'external_id': tools.ustr(row[0]),
                'identification_id': tools.ustr(row[1]),
                'name': tools.ustr(row[2]),
                'code': tools.ustr(row[0]),
                'work_phone': row[7],
                'gender': 'female' if row[3] == 'F' else 'male',
                'place_of_birth': tools.ustr(row[12]) if row[12] not in ['', None, False] else '',
                'admission_date': fields.Date.to_string(row[13]),
                'country_id': country.id,
                'race': race[row[8]],
                'marital': marital_status.get(row[9], ''),
                'political_affiliation': political_affiliations[row[11]] if row[11] else political_affiliations['No Militante'],
                'birthday': row[10],
                'department_id': departments_dict.get((row[5] + '-' + row[6]).strip(), False),
                'job_id': jobs_dict.get((row[6]+row[5]+row[4]).strip(), False),
                'defence_location_id': defence_locations_dict.get(row[14], False),
                'defence_situation': tools.ustr(row[15]),
                'school_level_id': school_levels_dict.get(row[16], False),
                'active': True,
                'company_id': self.get_company(str(row[6]))
            }

            employee = employee_obj.search([('external_id', '=', row[0]), ('active', '=', False)], limit=1)

            if len(employee) == 0:
                address_home = self.add_address(tools.ustr(row[2]),tools.ustr(row[17]), country.id, tools.ustr(row[18]), tools.ustr(row[19]), None)
                employee_data['address_home_id'] = address_home
                employee_obj.create(employee_data)
                _logger.info("Imported employee: %s." % (tools.ustr(employee_data['name']),))
            else:
                if employee.address_home_id:
                    self.add_address(tools.ustr(row[2]), tools.ustr(row[17]), country.id, tools.ustr(row[18]), tools.ustr(row[19]), employee.address_home_id.id)
                else:
                    address_home = self.add_address(tools.ustr(row[2]), tools.ustr(row[17]), country.id, tools.ustr(row[18]), tools.ustr(row[19]), None)
                    employee_data['address_home_id'] = address_home
                employee.with_context(no_create_movement=True).write(employee_data)
                _logger.info("Updated employee: %s." % (tools.ustr(employee_data['name']),))
        return True

    def add_address(self, name, street, country_id, prov, munic, id):

        state_obj = self.env['res.country.state']
        state_id = None
        state = state_obj.search([('name', '=', prov),('country_id', '=', country_id)],limit=1)
        if len(state) > 0:
            state_id = state.id

        municipality_id = None
        if state_id:
            municipality_obj = self.env['l10n_cu_base.municipality']
            municipality = municipality_obj.search([('name', '=', munic), ('state_id', '=', state_id)],limit=1)
            if len(municipality) > 0:
                municipality_id = municipality.id

        partner_data = {
            'name': name,
            'street': street,
            'country_id': country_id,
            'state_id': state_id,
            'municipality_id': municipality_id,
            'employee': False,#la direccion del empleado no es un empleado
            'active': True
        }
        partner_obj = self.env['res.partner']
        if id == None:
           obj = partner_obj.create(partner_data)
           return obj.id
        else:
           partner = partner_obj.search([('id', '=', id)])
           return partner.write(partner_data)

    def import_departments(self, connection):
        department_obj = self.env['hr.department']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT  Id_Departamento, Id_Area, NombreDepartamento FROM CPT_Departamentos;""")
        except Exception, e:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        for row in cursor:
            department_data = {'name': tools.ustr(row[2]), 'external_id': tools.ustr(row[0] + '-' + row[1]), 'company_id': self.get_company(str(row[1]))}
            department = department_obj.search([('external_id', '=', tools.ustr(row[0] + '-' + row[1]))], limit=1)

            if len(department) == 0:
                department_obj.create(department_data)
            else:
                department.write(department_data)

        cursor.close()
        return True

    @api.one
    def import_employees_schedule(self, connection):
        schedule_turn_obj = self.env['resource.calendar.attendance']
        schedule_obj = self.env['resource.calendar']
        employee_obj = self.env['hr.employee']
        employees = employee_obj.search([])

        cursor = connection.cursor()
        # Importing Schedules...
        schedule_data = {}
        schedules = schedule_obj.sudo().search([])
        schedules_list = []

        for schedule in schedules:
            schedule_data[schedule.external_id] = schedule.id

        try:
            cursor.execute("SELECT Id_Horario, NombreHorario, FechaInicioHorario, TipoHorario "
                           "FROM CPT_Horarios;")
        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        for schedule in cursor:
            data = {
                'external_id': schedule[0],
                'name': schedule[1],
                'init_date': schedule[2],
                'background_average_hours': float(190.6),
                'background_average_days': float(24)
             }

            squedule = schedule_obj.search([('external_id', '=', schedule[0])], limit=1)

            if len(squedule) == 0:
                res = schedule_obj.sudo().create(data)
                schedule_data[schedule[0]] = res.id
                schedules_list.append(res)
            else:
                res = squedule.write(data)
                schedule_data[schedule[0]] = squedule.id
                schedules_list.append(squedule)

        for schedule in schedules_list:
            cursor.execute("""SELECT TurnosHorario.Id_Horario, TurnosHorario.Id_Turno, TurnosHorario.DiaTurno,
                                     Turno.HoraInicioTurno, Turno.HoraFinTurno, Turno.HoraDescansoTurno,
                                     Turno.TiempoDescansoTurno, Turno.NombreTurno
                              FROM CPT_TurnosHorario TurnosHorario
                              INNER JOIN CPT_Turnos Turno
                              ON TurnosHorario.Id_Turno = Turno.Id_Turno
                              WHERE Id_Horario = '%s';""" % (schedule.external_id,))

            for record in cursor:
                turns = schedule_turn_obj.sudo().search([
                    ('calendar_id', '=', schedule_data[record[0]]),
                    ('external_id', '=', record[1]),
                    ('dayofweek', '=', record[2] - 1)]
                )

                def to_float_time(value):
                    float_time_pair = value.split(":")
                    hours, minutes = float(float_time_pair[0]), float(float_time_pair[1])
                    return hours + (minutes / 60)

                def hours_time_string(hours):
                    """ convert a number of hours (float) into a string with format '%H:%M' """
                    minutes = int(round(hours * 60))
                    return "%02d:%02d" % divmod(minutes, 60)
                # Le quite la hora de fin a todos los horarios
                values = {
                    'name': tools.ustr(record[7]),
                    'dayofweek': str(record[2] - 1),
                    'date_from': record[3],
                    # 'date_to': record[4],
                    'hour_from': to_float_time(record[3].strftime("%H:%M")) if isinstance(record[3], datetime) else 0.0,
                    'hour_to': to_float_time(record[4].strftime("%H:%M")) if isinstance(record[4], datetime) else 0.0,
                    'rest_time': (float(record[6]) / 60)
                }

                if not len(turns):
                    values['calendar_id'] = schedule_data[record[0]]
                    values['external_id'] = record[1]
                    schedule_turn_obj.sudo().create(values)
                else:
                    turns.sudo().write(values)

        query = """SELECT Fecha, Id_Horario
                   FROM CPT_SecuenciaHorarios
                   WHERE Id_Empleado = %d
                   ORDER BY Fecha ASC"""

        for employee in employees:
            if employee.external_id:
                cursor.execute(query % (int(employee.external_id),))

                work_time_id = False
                for record in cursor:
                    work_time_id = record[1]

                if work_time_id:
                    employee.write({'calendar_id': schedule_data.get(work_time_id, False)})

        cursor.close()
        return True

    def import_employee_school_level(self, connection):
        school_level_obj = self.env['l10n_cu_hlg_hr.employee_school_level']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_Nivel, NombreNivel FROM CPT_NivelEscolaridad;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        for row in cursor:
            data = {'code': row[0], 'name': tools.ustr(row[1]), 'external_id': row[0]}
            school_level = school_level_obj.search([('external_id', '=', row[0])], limit=1)

            if len(school_level) == 0:
                school_level_obj.create(data)
            else:
                school_level.write(data)

        cursor.close()
        return True

    def import_employee_defence_location(self, connection):
        defence_location_obj = self.env['l10n_cu_hlg_hr.employee_defence_location_type']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_Ubicacion, NombreUbicacion FROM CPT_UbicacionDefensa;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

        for row in cursor:
            data = {'code': tools.ustr(row[1]), 'name': tools.ustr(row[1]), 'external_id': row[0]}
            locations = defence_location_obj.search([('external_id', '=', row[0])], limit=1)

            if len(locations) == 0:
                defence_location_obj.create(data)
            else:
                locations.write(data)

        cursor.close()
        return True

    def import_employee_jobs(self, connection):
        # Importing needed elements...
        position_obj = self.env['l10n_cu_hlg_hr.position']
        department_obj = self.env['hr.department']

        self.import_employee_position(connection)

        cursor = connection.cursor()
        job_obj = self.env['hr.job']

        try:
            cursor.execute("""SELECT CPT_Plantilla.Id_Area, CPT_Plantilla.Id_Departamento, CPT_Plantilla.Id_Cargo, CPT_Cargos.Id_GrupoSalarial, CPT_Cargos.Id_CategOcupacional, 
                                     CPT_Plantilla.Cantidad, CPT_Plantilla.Anterior,
                                     CPT_Cargos.NombreCargo, CPT_Plantilla.[Real]
                              FROM CPT_Plantilla
                              INNER JOIN CPT_Cargos ON CPT_Cargos.Id_Cargo = CPT_Plantilla.Id_Cargo;""")

        except Exception, e:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))


        positions = position_obj.search([])
        position_dict = {}

        for position in positions:
            position_dict[position.external_id] = position.id


        departments = department_obj.search([])

        departments_dict = {}
        for department in departments:
            departments_dict[department.external_id] = department.id

        for row in cursor:
            name_temp = tools.ustr(row[7])
            name = name_temp if len(name_temp) and name_temp[0] != '*' else name_temp[1:]
            data = {'name': name,
                    'code': row[2],
                    'external_id': row[0] + row[1] + row[2],
                    'position_id':position_dict.get(row[2]+ '-' + row[3]+ '-' + row[4], False),
                    'department_id':departments_dict.get(row[1] + '-' + row[0]),
                    'company_id': self.get_company(str(row[0]))
                    }


            jobs = job_obj.search([('external_id', '=', row[0] + row[1] + row[2])], limit=1)

            if len(jobs) == 0:
                job_obj.create(data)
                _logger.info("Imported employee's job: %s." % (tools.ustr(data['name']),))
            else:
                jobs.write(data)
                _logger.info("Updated employee's job: %s." % (tools.ustr(data['name']),))

        cursor.close()
        return True

    def import_employee_position(self,connection):
        school_level_obj = self.env['l10n_cu_hlg_hr.employee_school_level']
        salary_group_obj = self.env['l10n_cu_hlg_hr.salary_group']
        position_obj = self.env['l10n_cu_hlg_hr.position']

        self.import_position_salary_group(connection)
        self.import_employee_school_level(connection)

        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_Cargo, NombreCargo, Id_GrupoSalarial, Id_CategOcupacional, CLA, OTROS,
                                   NumeroOrden, Id_Nivel
                              FROM CPT_Cargos;""")

        except Exception, e:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                  and make sure to select the correct one..."""))

        school_levels = school_level_obj.search([])
        school_level_dict = {}

        for school_level in school_levels:
            school_level_dict[school_level.external_id] = school_level.id

        salary_groups = salary_group_obj.search([])
        salary_group_dict = {}

        for salary_group in salary_groups:
            salary_group_dict[salary_group.external_id] = salary_group.id

        for row in cursor:
            name_temp = tools.ustr(row[1])
            name = name_temp if len(name_temp) and name_temp[0] != '*' else name_temp[1:]
            print name
            data = {
                'name': name,
                'salary_group_id': salary_group_dict.get(row[2] + '-' + row[3], False),
                'school_level_id': school_level_dict.get(row[7], False),
                'external_id': row[0] + '-' + row[2] + '-' + row[3]
            }

            positions = position_obj.search([('external_id', '=', row[0] + '-' + row[2] + '-' + row[3])], limit=1)
            if len(positions) == 0:
                position_obj.create(data)
            else:
                position_obj.write(data)

        cursor.close()
        return True

    def import_position_salary_group(self, connection):
        salary_scale_obj = self.env['l10n_cu_hlg_hr.salary_scale']
        salary_group_obj = self.env['l10n_cu_hlg_hr.salary_group']
        occupational_category_obj = self.env['l10n_cu_hlg_hr.occupational_category']
        cursor = connection.cursor()

        self.import_job_salary_scale(connection)
        self.import_job_occupational_category(connection)

        try:
            cursor.execute("""SELECT Id_GrupoSalarial, Id_CategOcupacional, Escala, EscalaMedio, EscalaMaximo
                               FROM CPT_GruposSalariales;""")
        except Exception, e:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                  and make sure to select the correct one..."""))

        salary_scales = salary_scale_obj.search([])
        salary_scale_dict = {}

        for salary_scale in salary_scales:
            salary_scale_dict[salary_scale.name] = salary_scale.id

        occupational_categories = occupational_category_obj.search([])
        occupational_categories_dict = {}

        for occupational_category in occupational_categories:
            occupational_categories_dict[occupational_category.external_id] = occupational_category.id

        for row in cursor:
            data = {
                'scale_salary': row[2],
                'salary_scale_id': salary_scale_dict.get(row[0], False),
                'occupational_category_id': occupational_categories_dict.get(tools.ustr(row[1]), False),
                'external_id': row[0] + '-' + row[1]
            }

            salary_groups = salary_group_obj.search([('external_id', '=', row[0] + '-' + row[1])], limit=1)
            if len(salary_groups) == 0:
                salary_group_obj.create(data)
            else:
                salary_groups.write(data)

        cursor.close()
        return True

    def import_job_occupational_category(self, connection):
        job_occupational_category_obj = self.env['l10n_cu_hlg_hr.occupational_category']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_CategOcupacional, NombreCategOcupacional, Orden FROM CPT_CategOcupacionales;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                  and make sure to select the correct one..."""))

        for row in cursor:
            data = {
                'code': row[0].strip(),
                'name': tools.ustr(row[1]),
                'external_id': row[0].strip(),
                'order': row[2]
            }

            job_occupational_category = job_occupational_category_obj.search(
                [('external_id', '=', tools.ustr(row[0].strip()))], limit=1
            )

            if len(job_occupational_category) == 0:
                job_occupational_category_obj.create(data)
            else:
                job_occupational_category.write(data)

        cursor.close()
        return True

    def import_job_salary_scale(self, connection):
        job_salary_scale_obj = self.env['l10n_cu_hlg_hr.salary_scale']
        cursor = connection.cursor()

        try:
            cursor.execute("""SELECT Id_GrupoSalarial FROM CPT_GruposSalariales;""")

        except Exception:
            cursor.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                         and make sure to select the correct one..."""))

        for row in cursor:
            data = {
                'name': tools.ustr(row[0]),
            }

            job_salary_scale = job_salary_scale_obj.search(
                [('name', '=', row[0])], limit=1
            )

            if len(job_salary_scale) == 0:
                job_salary_scale_obj.create(data)
            else:
                job_salary_scale_obj.write(data)

        cursor.close()
        return True
