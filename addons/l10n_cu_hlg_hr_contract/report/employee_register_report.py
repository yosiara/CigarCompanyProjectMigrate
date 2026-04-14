# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
import unicodedata

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.'),
          'invalidmod':_('You are using a invalid key. Please contact the suport center for a new one.'),}

def cal_porciento(P, B):
    p = 0
    if P > 0:
       p = float(B) / float(P) * 100
    return format(p, '.2f')

class ParticularReport(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.employee_register'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.employee_register')
        doc_obj = self.env[report.model].search([],order='name')
        
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_model_list': doc_obj,

        }
        return report_obj.render('l10n_cu_hlg_hr_contract.employee_register', docargs)
    
class EmployeeReport(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.by_employee_register'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.by_employee_register')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        doc_obj = self.env['hr.contract'].search([('state', '=', 'approved'), ('clasification', '=', 'framework'),
                                                  ('contract_type', '=', 'indeterminate')]).sorted(
            key=lambda a: a.job_id.name)
        temp = []
        # retributions = self.env['hr.retributions.deductions'].search([
        #     ('type', '=', 'more'),
        # ])
        for contract in doc_obj:
            contract_retributions = contract.retributions_deductions_ids
            con = {'contract':contract,'retribs':{}}
            
            
            # for retrib in retributions:
            #     for r in contract_retributions:
            #         if retrib.id == r.id:
            #             con.get('retribs').update({retrib.id:r.amount})
            #         else:
            #             con.get('retribs').update({retrib.id: ""})
            #     else:
            #         con.get('retribs').update({retrib.id: con.get('retribs').get(retrib.id,False) or ""})
                        
            temp.append(con)

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_model_list': temp

        }
        return report_obj.render('l10n_cu_hlg_hr_contract.by_employee_register', docargs)

class JobByCategory(models.AbstractModel):
        _name = 'report.l10n_cu_hlg_hr_contract.by_category_register'

        @api.multi
        def render_html(self, docids, data=None):
            report_obj = self.env['report']

            report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.by_category_register')

            # check_reg
            resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
            if resp != 'ok':
                raise ValidationError(resp_dic[resp])

            self.env.cr.execute("SELECT job.department_id, salary.occupational_category_id, \
                                 count(salary.occupational_category_id)as cat, count(job.department_id) as dep \
                                 FROM hr_job AS job \
                                 JOIN l10n_cu_hlg_hr_salary_group salary ON (salary.id = job.salary_group_id) \
                                 INNER JOIN l10n_cu_hlg_hr_salary_scale ON salary.salary_scale_id = l10n_cu_hlg_hr_salary_scale.id \
                                 GROUP BY salary.occupational_category_id, job.department_id, l10n_cu_hlg_hr_salary_scale.name  \
                                 ORDER BY l10n_cu_hlg_hr_salary_scale.name DESC")

            doc_obj = self.env.cr.dictfetchall()
            department_list = self.env['hr.department'].search([])
            categories_list = self.env['l10n_cu_hlg_hr.occupational_category'].search([])
            matrix = map(lambda a: dict({'id': a.id, 'name': a.name, 'values': {}}), department_list)
            matrix.append({'id': None, 'name': '-', 'values': {}})

            for category in categories_list:
                #values_of_category = filter(lambda a: a.get('occupational_category_id', False), doc_obj)
                for dep in matrix:
                    def filter_doc(a):
                        a_cat = a.get('occupational_category_id', False)
                        a_dep = a.get('department_id', '-')
                        if a_cat == category.id and a_dep == dep.get('id', "-"):
                            return True
                        else:
                            return False
                    values_of_category = filter(filter_doc, doc_obj)
                    if values_of_category and values_of_category[0]:
                        ele_cat = category.id
                        ele_cat_cant = values_of_category[0].get('cat')
                        old_value = dep.get('values', {}).get(ele_cat, 0)

                        dep.get('values', {}).update({ele_cat: old_value+ele_cat_cant})
                    else:
                        dep.get('values', {}).update({category.id: 0})

            matrix_final = map(lambda a: a.update({'total': sum(a.get('values',{}).itervalues())}), matrix)

            docargs = {
                'doc_ids': self._ids,
                'doc_model': report.model,
                'docs': self,
                'obj_model_list': doc_obj,
                'categories': categories_list,
                'matrix': matrix
            }
            return report_obj.render('l10n_cu_hlg_hr_contract.by_category_register', docargs)


class ApprovedTemplate(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.approved_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.approved_template')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT l10n_cu_hlg_hr_occupational_category.name, \
                             sum(COALESCE(hr_job.expected_employees,0)) as cantidad \
                             FROM hr_job \
                             RIGHT JOIN l10n_cu_hlg_hr_occupational_category \
                             ON hr_job.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                             GROUP BY l10n_cu_hlg_hr_occupational_category.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.approved_template', docargs)

class JobVacancies(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.vacancies'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.vacancies')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT hr_department.name AS department, hr_job.name AS job, l10n_cu_hlg_hr_occupational_category.name as category, \
                            Sum(hr_job.expected_employees - COALESCE(hr_job.counts_hired_employee,0)) AS cantidad, \
                            l10n_cu_hlg_hr_salary_scale.name AS scale \
                            FROM hr_job \
                            INNER JOIN l10n_cu_hlg_hr_occupational_category ON hr_job.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                            INNER JOIN l10n_cu_hlg_hr_salary_group ON l10n_cu_hlg_hr_salary_group.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                            INNER JOIN l10n_cu_hlg_hr_salary_scale ON l10n_cu_hlg_hr_salary_scale.id = l10n_cu_hlg_hr_salary_group.salary_scale_id  \
                            INNER JOIN hr_department ON hr_department.id = hr_job.department_id \
                            GROUP BY hr_department.name, hr_job.name, \
                            l10n_cu_hlg_hr_occupational_category.name, l10n_cu_hlg_hr_salary_scale.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.vacancies', docargs)

class JobApprovedCover(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.approved_cover'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.approved_cover')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT hr_job.name AS job, l10n_cu_hlg_hr_occupational_category.name as category, \
                             Sum(hr_job.expected_employees) AS approced, \
                             Sum( COALESCE(hr_job.counts_hired_employee,0)) AS cover, \
                             l10n_cu_hlg_hr_salary_scale.name AS scale \
                             FROM hr_job \
                             INNER JOIN l10n_cu_hlg_hr_occupational_category ON hr_job.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                             INNER JOIN l10n_cu_hlg_hr_salary_group ON l10n_cu_hlg_hr_salary_group.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                             INNER JOIN l10n_cu_hlg_hr_salary_scale ON l10n_cu_hlg_hr_salary_scale.id = l10n_cu_hlg_hr_salary_group.salary_scale_id \
                             GROUP BY hr_job.name, l10n_cu_hlg_hr_occupational_category.name, l10n_cu_hlg_hr_salary_scale.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.approved_cover', docargs)

class JobCurrentSituation(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.current_situation'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.current_situation')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT l10n_cu_hlg_hr_occupational_category.name AS category, \
                            Sum(hr_job.expected_employees) AS approced, \
                            Sum(COALESCE(hr_job.counts_hired_employee,0)) AS cover, \
                            Sum(hr_job.expected_employees - COALESCE(hr_job.counts_hired_employee,0)) AS vacancie, \
                            Sum(CASE WHEN hr_employee.gender= 'male' THEN 1 ELSE 0 END) AS male, \
                            Sum(CASE WHEN hr_employee.gender= 'female' THEN 1 ELSE 0 END) AS female \
                            FROM hr_job \
                            LEFT JOIN hr_contract ON hr_contract.job_id = hr_job.id  \
                            AND hr_contract.clasification = 'framework' \
                            AND hr_contract.contract_type = 'indeterminate' \
                            INNER JOIN l10n_cu_hlg_hr_occupational_category ON l10n_cu_hlg_hr_occupational_category.id = hr_job.occupational_category_id \
                            LEFT JOIN hr_employee ON hr_employee.id = hr_contract.employee_id \
                            GROUP BY l10n_cu_hlg_hr_occupational_category.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.current_situation', docargs)


class JobVacanciesTotal(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.vacancies_total'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.vacancies_total')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT hr_job.name AS job, l10n_cu_hlg_hr_occupational_category.name as category, \
                                Sum(hr_job.expected_employees - COALESCE(hr_job.counts_hired_employee,0)) AS cantidad, \
                                l10n_cu_hlg_hr_salary_scale.name AS scale \
                                FROM hr_job \
                                INNER JOIN l10n_cu_hlg_hr_occupational_category ON hr_job.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                                INNER JOIN l10n_cu_hlg_hr_salary_group ON l10n_cu_hlg_hr_salary_group.occupational_category_id = l10n_cu_hlg_hr_occupational_category.id \
                                INNER JOIN l10n_cu_hlg_hr_salary_scale ON l10n_cu_hlg_hr_salary_scale.id = l10n_cu_hlg_hr_salary_group.salary_scale_id  \
                                GROUP BY hr_job.name, \
                                l10n_cu_hlg_hr_occupational_category.name, l10n_cu_hlg_hr_salary_scale.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.vacancies_total', docargs)


class JobCoveredByCategories(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.covered_by_categories'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.covered_by_categories')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT l10n_cu_hlg_hr_occupational_category.name AS category, \
                                Sum(CASE WHEN hr_employee.gender= 'male' THEN 1 ELSE 0 END) AS male, \
                                Sum(CASE WHEN hr_employee.gender= 'female' THEN 1 ELSE 0 END) AS female, \
                                Sum(COALESCE(hr_job.counts_hired_employee,0)) AS cover \
                                FROM hr_job \
                                INNER JOIN hr_contract ON hr_contract.job_id = hr_job.id \
                                AND hr_contract.clasification = 'framework' \
                                AND hr_contract.contract_type = 'indeterminate' \
                                RIGHT JOIN l10n_cu_hlg_hr_occupational_category ON l10n_cu_hlg_hr_occupational_category.id = hr_job.occupational_category_id\
                                LEFT JOIN hr_employee ON hr_employee.id = hr_contract.employee_id \
                                GROUP BY l10n_cu_hlg_hr_occupational_category.name")

        doc_obj = self.env.cr.dictfetchall()

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.covered_by_categories', docargs)


class JobQualifiedWorkforce(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.qualified_workforce'

    def get_colunm_name(self, value):
        _value = value.strip().replace(" ", "_")
        _value = unicodedata.normalize("NFKD", _value).encode("ascii","ignore").decode("ascii")
        return _value

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.qualified_workforce')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        school_level_sql = ''
        school_level_col = []
        school_level_recs = self.env['l10n_cu_hlg_hr.employee_school_level'].search([])
        for school_level in school_level_recs:
            col_name = self.get_colunm_name(school_level.name)
            school_level_col.append(col_name)
            school_level_sql +=  "Sum(CASE WHEN l10n_cu_hlg_hr_position.school_level_id = " + str(school_level.id) + " THEN 1 ELSE 0 END) AS " +'"' + col_name + '",'

        sql = """SELECT l10n_cu_hlg_hr_occupational_category.name AS category, """ + school_level_sql + \
              """Sum(COALESCE(hr_job.expected_employees,0)) AS approced, 
              Sum(COALESCE(hr_job.counts_hired_employee,0)) AS cover 
              FROM hr_job
              RIGHT JOIN l10n_cu_hlg_hr_occupational_category ON l10n_cu_hlg_hr_occupational_category."id" = hr_job.occupational_category_id
              INNER JOIN l10n_cu_hlg_hr_position  ON hr_job.position_id = l10n_cu_hlg_hr_position."id" 
              GROUP BY l10n_cu_hlg_hr_occupational_category.name """

        self.env.cr.execute(sql)

        doc_obj = self.env.cr.dictfetchall()

        totals = {}
        i = 1
        for school_level in school_level_recs:
            totals[i] = 0
            for items in doc_obj:
                totals[i] = totals[i] + items[self.get_colunm_name(school_level.name)]
            i += 1

        CalPorciento = cal_porciento

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj,
            'school_level_thead': school_level_recs,
            'school_level_col': school_level_col,
            'Totals': totals,
            'get_cal_porciento': CalPorciento
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.qualified_workforce', docargs)


class GenaralInformation(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_contract.genaral_information'

    def get_academic_title(self, employee_id):
        obj = self.env['hr.employee'].browse(employee_id).academic_ids.filtered(lambda r: r['principal'] == True)
        result = {'title': '', 'anho': ''}
        if len(obj) > 0:
            result['title'] = obj.title_id.name
            result['anho'] = obj.end_date[0:4]
        return result

    def get_contract_type(self, type):
        CONTRACT_TYPE = {'determinate': 'DETERMINADO', 'indeterminate':'INDETERMINADO'}
        if type == 'determinate' or  type == 'indeterminate':
            return CONTRACT_TYPE[type]
        return ''

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_contract.genaral_information')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        obj = self.env['hr.employee']

        docargs = {
            'doc_ids': docids,
            'doc_model': report.model,
            'docs': obj.browse(docids),
            'get_academic_title': self.get_academic_title,
            'get_contract_type': self.get_contract_type
        }
        return report_obj.render('l10n_cu_hlg_hr_contract.genaral_information', docargs)