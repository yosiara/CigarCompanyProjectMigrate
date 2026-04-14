from odoo import api, models
from odoo.tools.translate import _
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT,DEFAULT_SERVER_DATE_FORMAT
resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.'),
          'invalidmod':_('You are using a invalid key. Please contact the suport center for a new one.'),}

report_name = 'l10n_cu_hlg_hr_contract.report'

SUPPLEMENT_TYPE = {'hire': _('Hire'),'fire': _('Fire'), 'change': _('Change')}

CONTRACT_TYPE = {'determinate':_('Determinate'),
                 'indeterminate':_('Indeterminate')}

SCHEDULE_PAY = {
            'monthly':_('Monthly'),
            'quarterly':_('Quarterly'),
            'semi-annually':_('Semi-annually'),
            'annually':_('Annually'),
            'weekly':_('Weekly'),
            'bi-weekly':_('Bi-weekly'),
            'bi-monthly':_('Bi-monthly')}

DAY_OF_WEEK = {'0': _('Monday'),
               '1': _('Tuesday'),
               '2': _('Wednesday'),
               '3': _('Thursday'),
               '4': _('Friday'),
               '5': _('Saturday'),
               '6': _('Sunday')}

MONTH_OF_YEAR = {'1': _('January'),
                 '2': _('February'),
                 '3': _('March'),
                 '4': _('April'),
                 '5': _('May'),
                 '6': _('June'),
                 '7': _('July'),
                 '8': _('August'),
                 '9': _('September'),
                 '10': _('October'),
                 '11': _('November'),
                 '12': _('December')}

def get_date(date):
    list = date.split('-')
    return list[2].split( )[0]+'-'+list[1]+'-'+list[0]

def get_days_duration(date_start,date_end):
    if date_start and date_end:
        dStart = datetime.strptime(date_start, DEFAULT_SERVER_DATE_FORMAT).date()
        dEnd = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        return (dEnd-dStart).days

def get_day_month_year(date_create):
    fecha = datetime.strptime(date_create,DEFAULT_SERVER_DATETIME_FORMAT)
    return fecha

def get_month(date_create):
    fecha = datetime.strptime(date_create,DEFAULT_SERVER_DATETIME_FORMAT)
    mes = MONTH_OF_YEAR[fecha.month.__str__()]
    return mes

def get_working_hours_shift(attendance):
    return attendance.hour_to - attendance.hour_from - attendance.rest_time

def get_attendances(attendances):
    result = []
    compare = []
    list_attendances = attendances.filtered(lambda att: att.hour_from > 0.0 and att.hour_to > 0.0)
    for att in list_attendances:
        name = att.name + str(att.hour_from) + str(att.hour_to)
        if not compare:
            result.append(att)
            compare.append(name)
        else:
            if name not in compare:
                result.append(att)
                compare.append(name)
    return result


def get_employee_autorized_sig(self,ids):
    return self.env['hr.employee'].browse(ids)

def get_employee_academic_ids(self,academic_ids):
    name = ""
    academics = self.env['hr.academic'].search([('id','in',academic_ids._ids),('principal','=',True)])
    if academics:
        name = academics[0].title_id.name
    return name

def get_list_retributions_deductions(text):
    result_list = []
    list_text = []
    if text:
        list_text = text.split(',')
    for elem in list_text:
        list_elem = elem.split('/')
        result_list.append({'name':list_elem[0],'amount': list_elem[1]})
    return result_list

class report_contract_indeterminate(models.AbstractModel):
    _name = 'report.' + report_name + '_indeterminate_contract'

    @api.multi
    def render_html(self, docids, data=None):
        docs = self.env['hr.contract'].search([('id', 'in', data['docids'])])
        report_obj = self.env['report']

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        get_format_date = get_date
        list_payment_method = self.env['hr_contract.payment_method'].search([('parent_id','=',False)])
        report = report_obj._get_report_from_name(report_name + '_indeterminate_contract')
        docargs = {
            'doc_ids': data['docids'],
            'doc_model': report.model,
            'docs': docs,
            'data':data,
            'get_date': get_format_date,
            'get_payment_method':list_payment_method,
            'CONTRACT_TYPE':CONTRACT_TYPE,
            'SCHEDULE_PAY':SCHEDULE_PAY,
            'authorized_signature': get_employee_autorized_sig,
            'self':self,
            'get_academic_title':get_employee_academic_ids,
            'get_datedaymonthyear': get_day_month_year,
            'get_month': get_month,
            'get_working_hours_shift': get_working_hours_shift,
            'get_attendances': get_attendances,
        }
        return self.env['report'].render(report_name + '_indeterminate_contract', docargs)

class report_contract_determinate(models.AbstractModel):
    _name = 'report.' + report_name + '_determinate_contract'

    @api.multi
    def render_html(self, docids, data=None):
        docs = self.env['hr.contract'].search([('id', 'in', data['docids'])])
        report_obj = self.env['report']

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        get_format_date = get_date
        list_payment_method = self.env['hr_contract.payment_method'].search([('parent_id','=',False)])
        report = report_obj._get_report_from_name(report_name + '_determinate_contract')
        docargs = {
            'doc_ids': data['docids'],
            'doc_model': report.model,
            'docs': docs,
            'data':data,
            'get_date': get_format_date,
            'get_payment_method':list_payment_method,
            'get_days_duration':get_days_duration,
            'SCHEDULE_PAY':SCHEDULE_PAY,
            'authorized_signature': get_employee_autorized_sig,
            'self':self,
            'get_academic_title': get_employee_academic_ids,
            'get_datedaymonthyear': get_day_month_year,
            'get_month': get_month,
            'get_working_hours_shift': get_working_hours_shift
        }
        return self.env['report'].render(report_name + '_determinate_contract', docargs)

class report_contract_supplement(models.AbstractModel):
    _name = 'report.' + report_name + '_supplement_contract'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        contracts = self.env['hr.contract'].search([('id', '=', docids)])

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        for contract in contracts:
            if contract.clasification == 'framework':
                docs = self.env['hr.contract'].search(
                    [('parent_id', '=', docids), ('clasification', '=', 'supplement')], order='id desc', limit=1)
                break
            else:
                docs = self.env['hr.contract'].search([('id', '=', docids)])
                break
        getday_month_year = get_day_month_year
        getmonth = get_month
        report = report_obj._get_report_from_name(report_name + '_supplement_contract')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': docs,
            'SUPPLEMENT_TYPE': SUPPLEMENT_TYPE,
            'DAY_OF_WEEK': DAY_OF_WEEK,
            'get_month': getmonth,
            'get_datedaymonthyear': getday_month_year,
            'get_working_hours_shift': get_working_hours_shift,
            'get_attendances': get_attendances
        }
        return self.env['report'].render(report_name + '_supplement_contract', docargs)

class report_contract_mov_nomina(models.AbstractModel):
    _name = 'report.' + report_name + '_mov_nomina_contract'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        contracts = self.env['hr.contract'].search([('id', '=', docids)])

        # check_reg
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_hr_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

        for contract in contracts:
            if contract.clasification == 'framework':
                docs = self.env['hr.contract'].search(
                    [('parent_id', '=', docids), ('clasification', '=', 'supplement')], order='id desc', limit=1)
                break
            else:
                docs = self.env['hr.contract'].search([('id', '=', docids)])
                break
        report = report_obj._get_report_from_name(report_name + '_supplement_contract')
        docargs = {
            'doc_ids': self.ids,
            'doc_model': report.model,
            'docs': docs,
            'get_date': get_date,
            'SCHEDULE_PAY':SCHEDULE_PAY,
            'get_list_retributions_deductions':get_list_retributions_deductions,
        }
        return self.env['report'].render(report_name + '_mov_nomina_contract', docargs)