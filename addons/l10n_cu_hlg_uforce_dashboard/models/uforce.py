# -*- coding: utf-8 -*-
##############################################################################
from odoo.http import request
import datetime
from datetime import date
from odoo import api, fields, models, _
import json
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class UforceDashboard(models.Model):
    _name = 'l10n_cu_hlg_uforce_dashboard.dashboard'
    _description = 'Uforce Dashboard'

    name = fields.Char("Name")

    @api.model
    def get_data_info(self):
        uid = request.session.uid
        cr = self.env.cr
        year = str(date.today())[0:4]
        data_info = []

        six_grade_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('external_id','=','006')],limit=1).id
        six_grade_level_count = self.env['hr.employee'].search_count([('school_level_id','=',six_grade_level_id)])
        six_grade_level_count_female = self.env['hr.employee'].search_count([('school_level_id', '=', six_grade_level_id),('gender','=','female')])
        six_grade_level_count_male = six_grade_level_count - six_grade_level_count_female

        nine_grade_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('external_id', '=', '009')],limit=1).id
        nine_grade_level_count = self.env['hr.employee'].search_count([('school_level_id', '=', nine_grade_level_id)])
        nine_grade_level_count_female = self.env['hr.employee'].search_count([('school_level_id', '=', nine_grade_level_id),('gender','=','female')])
        nine_grade_level_count_male = nine_grade_level_count - nine_grade_level_count_female

        twelve_grade_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('external_id', '=', '012')],limit=1).id
        twelve_grade_level_count = self.env['hr.employee'].search_count([('school_level_id', '=', twelve_grade_level_id)])
        twelve_grade_level_count_female = self.env['hr.employee'].search_count([('school_level_id', '=', twelve_grade_level_id), ('gender', '=', 'female')])
        twelve_grade_level_count_male = twelve_grade_level_count - twelve_grade_level_count_female

        tecnical_grade_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('external_id', '=', 'TMD')],limit=1).id
        tecnical_grade_level_count = self.env['hr.employee'].search_count([('school_level_id', '=', tecnical_grade_level_id)])
        tecnical_grade_level_count_female = self.env['hr.employee'].search_count([('school_level_id', '=', tecnical_grade_level_id), ('gender', '=', 'female')])
        tecnical_grade_level_count_male = tecnical_grade_level_count - tecnical_grade_level_count_female

        university_grade_level_id = self.env['l10n_cu_hlg_hr.employee_school_level'].search([('external_id', '=', 'UNI')], limit=1).id
        university_grade_level_count = self.env['hr.employee'].search_count([('school_level_id', '=', university_grade_level_id)])
        university_grade_level_count_female = self.env['hr.employee'].search_count([('school_level_id', '=', university_grade_level_id), ('gender', '=', 'female')])
        university_grade_level_count_male = university_grade_level_count - university_grade_level_count_female

        age_range_one_id = self.env['l10n_cu_hlg_uforce.age_range'].search([('code', '=', '2920')], limit=1).id
        age_range_one_count = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_one_id)])
        age_range_one_count_female = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_one_id),('gender', '=', 'female')])
        age_range_one_count_male = age_range_one_count - age_range_one_count_female


        age_range_two_id = self.env['l10n_cu_hlg_uforce.age_range'].search([('code', '=', '2921')], limit=1).id
        age_range_two_count = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_two_id)])
        age_range_two_count_female = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_two_id), ('gender', '=', 'female')])
        age_range_two_count_male =  age_range_two_count - age_range_two_count_female

        age_range_three_id = self.env['l10n_cu_hlg_uforce.age_range'].search([('code', '=', '2922')], limit=1).id
        age_range_three_count = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_three_id)])
        age_range_three_count_female = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_three_id), ('gender', '=', 'female')])
        age_range_three_count_male = age_range_three_count - age_range_three_count_female


        age_range_four_id = self.env['l10n_cu_hlg_uforce.age_range'].search([('code', '=', '2923')], limit=1).id
        age_range_four_count = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_four_id)])
        age_range_four_count_female = self.env['hr.employee'].search_count([('age_range_id', '=', age_range_four_id), ('gender', '=', 'female')])
        age_range_four_count_male = age_range_four_count - age_range_four_count_female

        categ_directivos_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code','=','DIR')],limit=1).id
        categ_directivos_count = self.env['hr.employee'].search_count([('occupational_category_id','=',categ_directivos_id )])

        categ_dsuperior_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', 'DS')], limit=1).id
        categ_dsuperior_count = self.env['hr.employee'].search_count(
            [('occupational_category_id', '=', categ_dsuperior_id)])

        categ_servicios_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code','=','SER')], limit=1).id
        categ_servicios_count = self.env['hr.employee'].search_count([('occupational_category_id', '=', categ_servicios_id)])

        categ_tecnicos_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', 'TEC')], limit=1).id
        categ_tecnicos_count = self.env['hr.employee'].search_count([('occupational_category_id', '=', categ_tecnicos_id)])

        categ_obreros_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', 'OBR')], limit=1).id
        categ_obreros_count = self.env['hr.employee'].search_count([('occupational_category_id', '=', categ_obreros_id)])

        categ_operarios_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', 'OP')], limit=1).id
        categ_operarios_count = self.env['hr.employee'].search_count(
            [('occupational_category_id', '=', categ_operarios_id)])

        categ_estudiantes_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', '00')], limit=1).id
        categ_estudiantes_count = self.env['hr.employee'].search_count([('occupational_category_id', '=', categ_estudiantes_id)])

        categ_ejecutivos_id = self.env['l10n_cu_hlg_hr.occupational_category'].search(
            ['|', ('code', '=', 'E'), ('code', '=', 'E')], limit=1).id
        categ_ejecutivos_count = self.env['hr.employee'].search_count(
            [('occupational_category_id', '=', categ_ejecutivos_id)])

        categ_adm_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', 'ADM')],                                                                                       limit=1).id
        categ_adm_count = self.env['hr.employee'].search_count(
            [('occupational_category_id', '=', categ_adm_id)])

        categ_undefined_id = self.env['l10n_cu_hlg_hr.occupational_category'].search([('code', '=', '')], limit=1).id
        categ_undefined_id_count = self.env['hr.employee'].search_count(
            [('occupational_category_id', '=', categ_undefined_id )])

        categ_ocup_list = []
        categ_ocup_list.append(categ_directivos_count)
        categ_ocup_list.append(categ_dsuperior_count)
        categ_ocup_list.append(categ_servicios_count)
        categ_ocup_list.append(categ_tecnicos_count)
        categ_ocup_list.append(categ_obreros_count)
        categ_ocup_list.append(categ_operarios_count)
        categ_ocup_list.append(categ_estudiantes_count)
        categ_ocup_list.append(categ_ejecutivos_count)
        categ_ocup_list.append(categ_adm_count)
        categ_ocup_list.append(categ_undefined_id_count)

        categs_labels = ['Directivo','Directivo Superior' ,'Servicio','Técnico','Obrero','Operario','Estudiante','Ejecutivo','Administrativo', 'Sin Categoría Ocupacional Definida']

        #search the top five counts degree
        query_top_five = """
                                select count(hr_employee.degree_id) as cantidad,l10n_cu_hlg_uforce_degree.name  from hr_employee,l10n_cu_hlg_uforce_degree where hr_employee.degree_id is not null 
                                and hr_employee.degree_id = l10n_cu_hlg_uforce_degree.id group by hr_employee.degree_id,l10n_cu_hlg_uforce_degree.name  order by cantidad desc;
                            """
        cr.execute(query_top_five, )
        top_five_degree_count = cr.fetchall()

        top_five_list = []
        top_five_labels = []
        i = 0
        for tf in top_five_degree_count:
            if i < 5:
                top_five_list.append(tf[0])
                top_five_labels.append(tf[1])
                i+=1
            else:
                break

        view_uforce_id = self.env.ref('l10n_cu_hlg_uforce_dashboard.uforce_tree_dashboard').id

        data = {
            'view_uforce_id': view_uforce_id,
            'six_grade_level_count': six_grade_level_count,
            'nine_grade_level_count': nine_grade_level_count,
            'twelve_grade_level_count': twelve_grade_level_count,
            'tecnical_grade_level_count': tecnical_grade_level_count,
            'university_grade_level_count': university_grade_level_count,
            'age_range_one_count': age_range_one_count,
            'age_range_two_count': age_range_two_count,
            'age_range_three_count': age_range_three_count,
            'age_range_four_count': age_range_four_count,
            'age_range_one_count_female': age_range_one_count_female,
            'age_range_two_count_female': age_range_two_count_female,
            'age_range_three_count_female': age_range_three_count_female,
            'age_range_four_count_female': age_range_four_count_female,
            'age_range_one_count_male': age_range_one_count_male,
            'age_range_two_count_male': age_range_two_count_male,
            'age_range_three_count_male': age_range_three_count_male,
            'age_range_four_count_male': age_range_four_count_male,
            'six_grade_level_count_female': six_grade_level_count_female,
            'nine_grade_level_count_female': nine_grade_level_count_female,
            'twelve_grade_level_count_female': twelve_grade_level_count_female,
            'tecnical_grade_level_count_female': tecnical_grade_level_count_female,
            'university_grade_level_count_female': university_grade_level_count_female,
            'six_grade_level_count_male': six_grade_level_count_male,
            'nine_grade_level_count_male': nine_grade_level_count_male,
            'twelve_grade_level_count_male': twelve_grade_level_count_male,
            'tecnical_grade_level_count_male': tecnical_grade_level_count_male,
            'university_grade_level_count_male': university_grade_level_count_male,
            'categ_ocup_list':  categ_ocup_list,
            'categs_labels': categs_labels,
            'top_five_list': top_five_list,
            'top_five_labels': top_five_labels,
        }
        data_info.append(data)
        return data_info