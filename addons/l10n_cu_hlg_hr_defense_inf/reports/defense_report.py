# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.'),
          'invalidmod': _('You are using a invalid key. Please contact the suport center for a new one.'),
          }

def cal_porciento(P, B):
    p = 0
    if P > 0:
       p = float(B) / float(P) * 100
    return format(p, '.2f')

def Sexo(sex, tipo='C'):
    result_c = 'No definido'
    result_l = 'No definido'
    if sex == 'male':
        result_c = 'M'
        result_l = 'Masculino'
    elif sex == 'female':
        result_c = 'F'
        result_l = 'Femenino'
    if tipo == 'C':
        return result_c
    else:
        return result_l

class ConciliationMilitary(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_defense_inf.conciliation_military'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_defense_inf.conciliation_military')
		
		# check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT COALESCE(d.name,'No definido') as localizacion, \
                            Count(*) AS cantidad \
                            FROM hr_employee e \
                            LEFT JOIN l10n_cu_hlg_hr_employee_defence_location_type d ON d.id = e.defence_location_id \
                            WHERE COALESCE(e.is_indispensable_employee, FALSE) = FALSE \
                            GROUP BY d.name \
                            UNION ALL \
                            SELECT 'Imprescindibles' as localizacion, \
                            Count(*) AS cantidad \
                            FROM hr_employee e \
                            LEFT JOIN l10n_cu_hlg_hr_employee_defence_location_type d ON d.id = e.defence_location_id \
                            WHERE COALESCE(e.is_indispensable_employee, FALSE) = TRUE \
                            GROUP BY d.name")

        doc_obj = self.env.cr.dictfetchall()

        self.env.cr.execute("SELECT COALESCE(gender, 'No definido') as sexo, \
                                           count(*) as cantidad \
                                           FROM hr_employee \
                                           GROUP BY gender")

        doc_sex_obj = self.env.cr.dictfetchall()

        call_sexo = Sexo

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj,
            'sex_list': doc_sex_obj,
            'get_sexo': call_sexo
        }
        return report_obj.render('l10n_cu_hlg_hr_defense_inf.conciliation_military', docargs)


class MilitatyRegistry(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_defense_inf.military_registry'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_defense_inf.military_registry')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT COALESCE(d.name,'No definido') as localizacion, \
                                   Count(*) AS cantidad \
                                   FROM hr_employee e \
                                   LEFT JOIN l10n_cu_hlg_hr_employee_defence_location_type d ON d.id = e.defence_location_id \
                                   WHERE COALESCE(e.is_indispensable_employee, FALSE) = FALSE \
                                   GROUP BY d.name \
                                   UNION ALL \
                                   SELECT 'Imprescindibles' as localizacion, \
                                   Count(*) AS cantidad \
                                   FROM hr_employee e \
                                   LEFT JOIN l10n_cu_hlg_hr_employee_defence_location_type d ON d.id = e.defence_location_id \
                                   WHERE COALESCE(e.is_indispensable_employee, FALSE) = TRUE \
                                   GROUP BY d.name")

        doc_obj = self.env.cr.dictfetchall()

        total_employee = self.env['hr.employee'].search_count([])
        total_in_defence = self.env['hr.employee'].search_count([('defence_location_id', '!=', 'NULL')])

        porciento = cal_porciento(total_in_defence, total_employee)

        CalPorciento = cal_porciento

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj,
            'por_ciento': porciento,
            'total_in_defence': total_in_defence,
            'total_employee': total_employee,
            'get_cal_porciento': CalPorciento
        }
        return report_obj.render('l10n_cu_hlg_hr_defense_inf.military_registry', docargs)


class MilitatyRegistryList(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_defense_inf.military_registry_list'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']

        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_defense_inf.military_registry_list')

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        self.env.cr.execute("SELECT COALESCE(d.name, 'No incorporado') as defence, resource_resource.code, \
                             hr_employee.name_related, hr_employee.identification_id, hr_employee.gender, \
                             hr_job.name AS job, hr_department.name AS department, hr_employee.mobile_phone \
                             FROM resource_resource \
                             INNER JOIN hr_employee ON hr_employee.resource_id = resource_resource.id \
                             LEFT JOIN l10n_cu_hlg_hr_employee_defence_location_type AS d ON d.id = hr_employee.defence_location_id \
                             INNER JOIN hr_job ON hr_employee.job_id = hr_job.id \
                             INNER JOIN hr_department ON hr_employee.department_id = hr_department.id \
                             AND hr_job.department_id = hr_department.id \
                             WHERE resource_resource.active = TRUE ORDER BY hr_employee.defence_location_id")

        doc_obj = self.env.cr.dictfetchall()

        call_sexo = Sexo

        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'obj_list': doc_obj,
            'get_sexo': call_sexo
        }
        return report_obj.render('l10n_cu_hlg_hr_defense_inf.military_registry_list', docargs)


class WearTemplate(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_defense_inf.wear_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_defense_inf.wear_template')
        obj = self.env['l10n_cu_hlg_hr_defense_inf.template_wear']

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        res = []
        j=1
        for item in obj.search([]):
            for i in range(item.number_of_places)[::-1]:
                vals = { 'no': j,
                         'job': item.position_id.name,
                         'salary_group': item.position_id.salary_group_id.salary_scale_id.name,
                         'occupational_category':  item.position_id.occupational_category_id.name,
                         'salary': item.position_id.salary,
                         'time_in_days': item.time_in_days
                         }
                res.append(vals)
                j = j + 1
                print i


        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': obj.search([]),
            'get_list': res
        }
        return report_obj.render('l10n_cu_hlg_hr_defense_inf.wear_template', docargs)

class InvasionTemplate(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_hr_defense_inf.invasion_template'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('l10n_cu_hlg_hr_defense_inf.invasion_template')
        obj = self.env['l10n_cu_hlg_hr_defense_inf.template_invasion']

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        res = []
        j=1
        for item in obj.search([]):
            for i in range(item.number_of_places)[::-1]:
                vals = { 'no': j,
                         'job': item.position_id.name,
                         'salary_group': item.position_id.salary_group_id.salary_scale_id.name,
                         'occupational_category':  item.position_id.occupational_category_id.name,
                         'salary': item.position_id.salary,
                         'time_in_days': item.time_in_days
                         }
                res.append(vals)
                j = j + 1
                print i


        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': obj.search([]),
            'get_list': res
        }
        return report_obj.render('l10n_cu_hlg_hr_defense_inf.invasion_template', docargs)

