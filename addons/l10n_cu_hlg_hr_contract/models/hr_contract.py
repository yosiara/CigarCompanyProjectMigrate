#-*- coding:utf-8 -*-

from datetime import datetime, timedelta
from odoo.exceptions import ValidationError, Warning
from odoo import fields, models, api, _
from lxml import etree
from odoo.osv.orm import setup_modifiers

CONTRACT_TYPE = [('determinate', _('DETERMINADO')),
                 ('indeterminate', _('INDETERMINADO'))]

SCHEDULE_PAY = ([
            ('monthly', _('Monthly')),
            ('quarterly', _('Quarterly')),
            ('semi-annually', _('Semi-annually')),
            ('annually', _('Annually')),
            ('weekly', _('Weekly')),
            ('bi-weekly', _('Bi-weekly')),
            ('bi-monthly', _('Bi-monthly'))])

MEANS_OF_PAYMENT = ([
            ('card', _('Card')),
            ('cash', _('Cash'))])

SUPPLEMENT_TYPE = [('hire', _('Hire')),
                   ('fire', _('Fire')),
                   ('change', _('Change'))]

CLASIFICATION = [('on_time', _('On time')),
                ('by_performance', _('By performance')),
                ]

class ContractPaymentMethod(models.Model):
    _name = "hr_contract.payment_method"
    _description = "Payment Method"

    name = fields.Char(required=True)
    code = fields.Char(required=True)  # For internal identification
    parent_id = fields.Many2one('hr_contract.payment_method', string='Parent Payment Method')

    child_ids = fields.One2many('hr_contract.payment_method', 'parent_id', string='Child Payment Method')
    description = fields.Text('Description')

    clasification = fields.Selection(CLASIFICATION, string='Clasification')
    contract_ids = fields.Many2many('hr.contract',
                                      'payment_method_contract_rel',
                                      string='Contracts')
    background_average = fields.Boolean('Background average',help='If it is true the form of payment will require a background average in days and hours.')


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    work_hours_day = fields.Float(string="Work hours per day")
    work_hours_average = fields.Float(string="Week average work hours")
    rest_time = fields.Float(string="Lunch break")
    monthly_average = fields.Float(string="Month average work hours")
    background_average_days = fields.Float(string='Background average time (days)')
    background_average_hours = fields.Float(string='Background average time(hours)')


class ContractType(models.Model):
    _inherit = "hr.contract.type"

    name = fields.Char('Contract Reference', translate=True)
    extras_hours = fields.Boolean(string="Extra hours", default=False)
    night_hours = fields.Boolean(string="Night hours", default=False)
    working_hours_ids_id = fields.Many2one('resource.calendar',
                                           string='Working hours')
    code = fields.Char(string='Code')
    retributions_ids = \
        fields.Many2many('hr_contract.retributions_deductions',
                         'ret_ded_contract_type_rel',
                         string='Contributions and Deductions')


class Contract(models.Model):
    _inherit = "hr.contract"

    @api.depends('date_start', 'date_end')
    def _compute_contract_type(self):
        for elem in self:
            if elem.date_start and elem.date_end:
                elem.contract_type = 'determinate'
            else:
                elem.contract_type = 'indeterminate'

    @api.one
    @api.depends('occupational_category_id')
    def _current_work_area(self):
        self.current_work_area = self.employee_id.company_id.name
        if self.occupational_category_id:
            self.current_work_area += " (" + self.occupational_category_id.name + ") "
        if self.department_id:
            self.current_work_area += " /" + self.department_id.name

    @api.depends('retributions_deductions_ids', 'wage')
    def compute_total(self):
        for elem in self:
            total = elem.wage
            for retrieve in elem.retributions_deductions_ids:
                if retrieve.show_in_contract:
                    total += retrieve.amount or 0
            elem.total_payment = total

    @api.depends('job_id')
    def compute_related_fields(self):
        for elem in self:
            if elem.job_id:
                elem.salary_group_id = elem.job_id.position_id.salary_group_id.salary_scale_id.id
                elem.wage = elem.job_id.position_id.salary_group_id.scale_salary
                elem.occupational_category_id = elem.job_id.position_id.salary_group_id.occupational_category_id.id

    # @api.onchange('type_id')
    # def onchange_type(self):
    #     for contract in self:
    #         record = contract.type_id.mapped('retributions_ids')
    #         contract.retributions_deductions_ids |= record

    #Framework
    salary_group_id = fields.Many2one('l10n_cu_hlg_hr.salary_scale',compute="compute_related_fields",
                                      string='Salary Group',
                                      track_visibility='onchange',store=True)

    department_id = fields.Many2one(track_visibility='onchange')

    wage = fields.Float(compute="compute_related_fields",string='Salary Scale', track_visibility='onchange',required=False,store=True)

    occupational_category_id = fields.Many2one('l10n_cu_hlg_hr.occupational_category',compute="compute_related_fields",
                                            string='Occupational Category',track_visibility='onchange',store=True)

    state = fields.Selection([('draft', 'Draft'),
                           ('approved', 'Approved'),
                           ('pending', 'To Closed'),
                           ('closed', 'Closed')], string='State', default='draft')

    current_work_area = fields.Char(compute='_current_work_area',
                                     string='Current work area', store = True)

    contract_type = fields.Selection(CONTRACT_TYPE,
                                     compute='_compute_contract_type',
                                     string='Contract type time', store = True,track_visibility='onchange')

    retributions_deductions_ids = \
        fields.Many2many('hr_contract.retributions_deductions',
                         'retributions_deductions_contract_rel',
                         string='Contributions and Deductions')

    total_payment = fields.Float(string='Total Payment',
                                 compute='compute_total',store=True)

    schedule_pay = fields.Selection(SCHEDULE_PAY, 'Schedule pay', default='monthly',track_visibility='onchange')

    payment_method_id = fields.Many2one('hr_contract.payment_method',string='Payment method',track_visibility='onchange')

    parent_id = fields.Many2one('hr.contract', string='Parent Contract')

    child_ids = fields.One2many('hr.contract','parent_id', string='Child Contracts')

    clasification = fields.Selection([('framework', 'Framework'), ('supplement', 'Supplement')],
                                     string='Clasification')

    supplement_count = fields.Integer( '# Supplement', compute='_compute_supplement_count')

    main = fields.Boolean('Main',track_visibility='onchange')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    last_supplement_id = fields.Many2one('hr.contract', compute='_compute_supplement_id', string='Last supplement',
                                         help='Latest contract of the employee', store=True)
    confirm_movement = fields.Boolean(default=False)

    #Supplement
    supplement_type = fields.Selection(SUPPLEMENT_TYPE, 'Movement type', default='hire')

    supplement_description = fields.Many2one('hr_contract.supplement_motive',
                                           string='Supplement Motive')

    supp_salary_group = fields.Char(string='Salary Group')

    supp_department = fields.Text('Department')

    supp_code_depart = fields.Char('Department code')

    supp_wage = fields.Float(string='Salary Scale')

    supp_occupational_category = fields.Text(string='Occupational Category')

    supp_payment_method = fields.Text(string='Payment method')

    supp_payment_method_class = fields.Text(string='Parent payment method clasification')

    supp_retributions_deductions = \
        fields.Text(string='Contributions and Deductions')

    supp_job = fields.Text('Job')

    supp_code_job = fields.Char('Job code')

    supp_type = fields.Text('Anormal Conditions')

    supp_working_hours = fields.Text('Working hours')

    supp_contract_type = fields.Text('Contract type time')

    means_of_payment = fields.Selection(MEANS_OF_PAYMENT, 'Means of payment', default='card')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.clasification == 'supplement':
                name = "%s / %s" % (name, record.job_id.name)
            result.append((record.id, name))
        return result

    def _get_working_hours(self,anormal_condition,date=False):
        if anormal_condition:
            return self.type_id.working_hours_ids_id
        return self.working_hours

    @api.constrains('payment_method_id','working_hours')
    def _validate_background_average(self):
        for elem in self:
            if elem.payment_method_id.background_average:
                if not elem.working_hours.background_average_days or elem.working_hours.background_average_days < 1:
                    raise ValidationError("The time background average time (days) must be greater than zero.")
                if not elem.working_hours.background_average_hours or elem.working_hours.background_average_hours < 1:
                    raise ValidationError("The time background average time (hours) must be greater than zero.")

    @api.constrains('employee_id','main','company_id')
    def _validate_contract_main_emp_com(self):
        Contract = self.env['hr.contract']
        for contract in Contract.search([]):
            if contract.clasification == 'framework':
                count = Contract.search_count([('employee_id','=',contract.employee_id.id),('main','=',True),('company_id','=',contract.company_id.id),('clasification','=','framework'),('state','=','approved')])
                count_indet = Contract.search_count([('employee_id', '=', contract.employee_id.id), ('contract_type', '=', 'indeterminate'),
                                               ('company_id', '=', contract.company_id.id),('clasification','=','framework'),('state','=','approved')])
                if count > 1 or count_indet > 1:
                    raise ValidationError(_("Each employee must have only one main or indeterminate contract per company"))

    @api.depends('child_ids')
    def _compute_supplement_id(self):
        """ get the lastest supplement """
        Contract = self.env['hr.contract']
        for contract in self:
            if contract.clasification == 'framework':
                contract.last_supplement_id = Contract.search([('parent_id', '=', contract.id),('clasification', '=', 'supplement')], order='id desc', limit=1)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        context = self._context or {}

        result = super(Contract, self).read(fields=fields, load=load)

        if context.get('rd') == 1:
            if 'retributions_deductions_ids' in fields:
                ids = result[0]['retributions_deductions_ids']
                result[0]['retributions_deductions_ids'] = self.env['hr_contract.retributions_deductions'].browse(
                    ids).filtered(lambda r: r['show_in_contract'] == True).ids

        return result

    @api.one
    @api.depends('child_ids.parent_id')
    def _compute_supplement_count(self):
        self.supplement_count = len(self.child_ids)

    @api.one
    def _get_type(self):
        type_ids = self.env.get('hr.contract.type').search([('name', '=', 'None')])
        return type_ids and type_ids[0] or False

    @api.multi
    def unlink(self):
        for contract in self:
            if contract.state != 'draft':
                raise ValidationError(_('You can not delete a contract in this state'))
        return super(Contract, self).unlink()

    @api.one
    @api.constrains('employee_id',)
    def _check_employee_age(self):
        if self.employee_id and self.employee_id.birthday:
            birthday = datetime.strptime(
                self.employee_id.birthday, '%Y-%m-%d')
            today = datetime.today()
            assert ((today-birthday).days > (365*15)), 'Age must be bigger than 15'

    def _get_retributions_deductions(self):
        retributions_deductions = ""
        for record in self.retributions_deductions_ids.filtered(lambda r: r['show_in_contract'] == True):
            if retributions_deductions == "":
                retributions_deductions = record.code + '-' + record.name + '/' + str(record.amount)
            else:
                retributions_deductions = retributions_deductions + ',' + record.code + '-' + record.name + '/' + str(record.amount)
        for ret_ded in self.type_id.retributions_ids:
            if ret_ded.id not in self.retributions_deductions_ids.ids:
                if retributions_deductions == "":
                    retributions_deductions = ret_ded.code + '-' + ret_ded.name + '/' + str(ret_ded.amount)
                else:
                    retributions_deductions = retributions_deductions + ',' + ret_ded.code + '-' + ret_ded.name + '/' + str(ret_ded.amount)
        return retributions_deductions

    @api.constrains('working_hours')
    def _validate_contract_working_hours(self):
        Contract = self.env['hr.contract']
        for contract in Contract.search([]):
            count = Contract.search_count([('id', '!=', contract.id), ('employee_id', '=', contract.employee_id.id),('working_hours', '=', contract.working_hours.id),('state', '=', 'approved'),('company_id','=',contract.company_id.id),('clasification','=','framework')])
            if count > 1:
                raise ValidationError(_("The employee already has an approved contract with the selected working schedule."))

    @api.multi
    def open_wzd(self, state=''):
        ctx = self._context.copy()
        ctx.update({'contract_id': self.id, 'state': state })
        action_rec = self.env['ir.model.data'].xmlid_to_object('l10n_cu_hlg_hr_contract.action_motive_movement_wzd')
        if action_rec:
            action = action_rec.read([])[0]
            action['context'] = ctx
            return action

    def create_supplement(self, motive_id, date_start, state_to_process):

        old_state = self.state
        self.write({'confirm_movement': False})
        old_last_supplement_id = self.last_supplement_id
        contract_type = None
        for elem in CONTRACT_TYPE:
            if self.contract_type == elem[0]:
                contract_type = elem[1]
        values = {'clasification': 'supplement',
                  'parent_id': self.id,
                  'state': 'approved',
                  'supp_salary_group': self.salary_group_id.name,
                  'supp_department': self.department_id.name,
                  'supp_code_depart': self.department_id.short_name,
                  'supp_wage': self.wage,
                  'supp_occupational_category': self.occupational_category_id.name,
                  'supp_payment_method': self.payment_method_id.name,
                  'supp_payment_method_class': self.payment_method_id.parent_id.clasification,
                  'supp_job': self.job_id.name,
                  'supp_code_job': self.job_id.code,
                  'supp_type': self.type_id.name,
                  'supp_working_hours': self.working_hours.name,
                  'supp_contract_type': contract_type,
                  'supplement_description': motive_id,
                  'date_start':date_start,
                  }

        date_from = fields.Datetime.from_string(date_start)
        if state_to_process in ['approved', 'pending']:
            if not self.child_ids:
                values['supplement_type'] = 'hire'
            else:
                values['supplement_type'] = 'change'

            if self.last_supplement_id.date_start < fields.Date.to_string(date_from - timedelta(days=1)):
                self.last_supplement_id.write(
                    {'date_end': fields.Date.to_string(date_from - timedelta(days=1)), 'state': 'closed'})
            else:
                raise ValidationError(_('Contract start date must be less than contract end date.'))

            supplement = self.copy(values)
            supplement.last_supplement_id = old_last_supplement_id.id
            if self.contract_type == 'determinate': supplement.date_end = False
            supplement.retributions_deductions_ids = self.retributions_deductions_ids
            supplement.supp_retributions_deductions = self._get_retributions_deductions()
            self.write({'state': state_to_process})
        if state_to_process == 'closed':
            if self.last_supplement_id and not self.last_supplement_id.supplement_description:
                raise ValidationError(_("You must enter a reason for your last payroll move"))

            date_end = fields.Date.to_string(date_from - timedelta(days=1))
            if self.last_supplement_id.date_start < fields.Date.to_string(date_from - timedelta(days=1)):
                self.last_supplement_id.write(
                    {'date_end': date_end, 'state': 'closed','supplement_type':'fire'})
            else:
                raise ValidationError(_('Contract start date must be less than contract end date.'))

            values['supplement_type'] = 'fire'
            if old_state != 'pending':
                supplement = self.copy(values)
                supplement.last_supplement_id = old_last_supplement_id.id
                supplement.date_end = fields.Date.to_string(date_from + timedelta(days=1))
            self.write({'state': state_to_process, 'date_end': date_end})
        return True
        

    @api.model
    def create(self, vals):
        if not vals.get('parent_id'):
            vals['clasification'] = 'framework'

        if vals.get('contract_type') == 'indeterminate':
            contract_main = self.env['hr.contract'].search(
                [('employee_id', '=', vals.get('employee_id')), ('main', '=', True),
                 ('company_id', '=', vals.get('company_id')),
                 ('clasification', '=', 'framework'), ('state', '=', 'approved'),('contract_type','=','determinate')])
            if contract_main and not vals.get('main') and vals.get('state') == 'approved':
                contract_main.write({'main': False})
                vals['main'] = True
        count_contract = self.env['hr.contract'].search(
            [('employee_id', '=', vals.get('employee_id')), ('company_id', '=', vals.get('company_id')),
             ('clasification', '=', 'framework')])
        if len(count_contract) == 0 and not vals.get('main') and vals.get('state') == 'approved':
            vals['main'] = True
        result = super(Contract, self).create(vals)
        if result.clasification == 'framework':
            # result.create_supplement()
            if result.main and result.state == 'approved':
                result.employee_id.write({'job_id': result.job_id.id,'department_id':result.department_id.id,'calendar_id':result.working_hours.id})
        return result

    @api.multi
    def write(self, vals):
        context = self._context or {}

        for contract in self:
            if 'retributions_deductions_ids' in vals and context.get('rd') == 1:
                ids = self.retributions_deductions_ids.ids
                obj = self.env['hr_contract.retributions_deductions']
                ids_not_show = obj.browse(ids).filtered(lambda r: r['show_in_contract'] == False).ids
                mylist = []
                if ids_not_show:
                    mylist = vals['retributions_deductions_ids'][0][2]
                    if len(vals['retributions_deductions_ids'][0][2]) != len(list(set(mylist).union(ids_not_show))):
                        vals['retributions_deductions_ids'][0][2] += ids_not_show

            if contract.state == 'closed' and 'state' in vals:
                raise ValidationError(_('You can not modify contract state in state closed'))
            if 'contract_type' in vals:
                contract_type = vals.get('contract_type')
            else:
                contract_type = contract.contract_type

            if 'employee_id' in vals:
                employee_id = vals.get('employee_id')
            else:
                employee_id = contract.employee_id.id

            if 'company_id' in vals:
                company_id = vals.get('company_id')
            else:
                company_id = contract.company_id.id

            if 'main' in vals:
                main = vals.get('main')
            else:
                main = contract.main

            if 'state' in vals:
                state = vals.get('state')
            else:
                state = contract.state

            if contract.state == 'approved' and 'state' not in vals and contract.clasification == 'framework':
                if 'confirm_movement' not in vals or ('confirm_movement' in vals and vals.get('confirm_movement')):
                    if context.get('call_of_import'):
                        vals['confirm_movement'] = False
                    else:
                        vals['confirm_movement'] = True
            if contract_type == 'indeterminate':
                contract_main = self.env['hr.contract'].search(
                    [('employee_id', '=', employee_id), ('main', '=', True),
                     ('company_id', '=', company_id),
                     ('clasification', '=', 'framework'), ('state', '=', 'approved'), ('id', '!=', contract.id),('contract_type','=','determinate')])
                if contract_main and not main and state == 'approved':
                    contract_main.write({'main': False})
                    vals['main'] = True
            count_contract = self.env['hr.contract'].search(
                [('employee_id', '=', employee_id), ('company_id', '=',company_id),
                 ('clasification', '=', 'framework')])
            if len(count_contract) == 1 and not main and state == 'approved':
                vals['main'] = True
            if contract.last_supplement_id and not contract.last_supplement_id.supplement_description:
                raise ValidationError(_("Debe introducir un motivo a su último movimiento de nómina"))
        result = super(Contract, self).write(vals)
        for contract in self:
            if contract.clasification == 'framework':
                if contract.main and contract.state == 'approved':
                    contract.employee_id.write({'job_id': contract.job_id.id,'department_id':contract.department_id.id,'calendar_id':contract.working_hours.id})
        return result

    @api.multi
    def btn_approved(self):
        return self.open_wzd('approved')

    @api.multi
    def btn_close(self):
        return self.open_wzd('closed')

    @api.multi
    def btn_pending(self):
        return self.open_wzd('pending')

    @api.multi
    def set_as_confirm(self):
        if self.clasification == 'framework':
           self.write({'confirm_movement': True})

    @api.multi
    def btn_change(self):
        return self.open_wzd('approved')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):

        res = super(Contract, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                    submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            # Set all fields read only when state is close.
            for node in doc.xpath("//field"):
                if node.get('name') in ['supp_contract_type','supp_wage','supp_department','supp_salary_group','supp_occupational_category','supp_working_hours','supp_type','supp_job','supp_payment_method','supp_retributions_deductions']:
                    node.set('readonly',"1")
                    node.set('attrs', "{'invisible': [('clasification','!=',('supplement'))]}")
                if node.get('name') in ['job_id','department_id','type_id','working_hours','payment_method_id','retributions_deductions_ids']:
                    node.set('attrs',"{'readonly': [('state', 'in', ('closed'))],'invisible': [('clasification', '==', ('supplement'))]}")
                if node.get('name') in ['salary_group_id','occupational_category_id','wage','contract_type']:
                    node.set('readonly','1')
                    node.set('attrs',"{'invisible': [('clasification', '==', ('supplement'))]}")
                if node.get('name') == 'state':
                    node.set('attrs', "{'readonly': [('state', 'in', ('closed'))],'invisible': [('clasification', '=', ('supplement'))]}")
                if node.get('name') in ['name','employee_id','trial_date_start','trial_date_end','date_start','advantages','schedule_pay']:
                    node.set('attrs', "{'readonly': ['|',('state', 'not in', ['draft']),('clasification', '=', 'supplement')]}")
                node_name = node.get('name')
                setup_modifiers(node, res['fields'][node_name])
            if 'supplement' in self._context and self._context.get('supplement'):
                doc.set('create','false')

        res['arch'] = etree.tostring(doc)
        return res


class AgreementParts(models.Model):
    _name = "l10n_cu_hlg_hr_contract.agreement_parts"

    name = fields.Char(string='Name', required="True")
    parts = fields.Selection([('employee', 'Employee'), ('employer', 'Employer'),('both', 'Employee and Employer')],
                                     string='Implicated Parts')


class SupplementMotive(models.Model):
    _name = "hr_contract.supplement_motive"

    name = fields.Char(string='Name',required="True")
    desc = fields.Text(string='Description')
    agreement_parts_id = fields.Many2one('l10n_cu_hlg_hr_contract.agreement_parts','Agreement parts')
    type = fields.Selection([('prov', 'Provisional'), ('perm', 'Permanente')],
                                     string='Type')


class EmployeeCategory(models.Model):
    _inherit = "hr.employee.category"

    payment_group = fields.Boolean("Payment Group")

    @api.multi
    @api.constrains('employee_ids')
    def _validate_employee(self):
        if self.payment_group:
            for employee in self.employee_ids:
                count = self.env['hr.employee.category'].search_count([('id','in',employee.category_ids._ids),
                                                                       ('payment_group','=',True)])
                if count > 1:
                    raise ValidationError(_("The employee '%s' must have only one category as a payment group") % (employee.name))


class Employee(models.Model):
    _inherit = "hr.employee"

    @api.depends('category_ids')
    def _get_payment_group(self):
        for record in self:
            for category in record.category_ids:
                if category.payment_group:
                    record.payment_group_id = category.id

    is_connected = fields.Boolean(string='Is Connected',
                                  compute='_compute_connected')
    date_of_admission = fields.Date('Date of admission', compute='_compute_admission_date')
    payment_group_id = fields.Many2one('hr.employee.category', 'Payment Group', compute='_get_payment_group',
                                       store=True)

    def _compute_admission_date(self):
        Contract = self.env['hr.contract']
        for employee in self:
            old_date = employee.date_of_admission
            new_date = Contract.search([('employee_id', '=', employee.id), ('clasification', '=', 'framework'), ('main', '=', True)],order='date_start',limit=1).date_start
            if new_date:
                employee.date_of_admission = new_date
            else: employee.date_of_admission = old_date

    @api.one
    def _compute_connected(self):
        self.is_connected = True if self.contract_id else False

    def _compute_contracts_count(self):
        # read_group as sudo, since contract count is displayed on form view
        contract_data = self.env['hr.contract'].sudo().read_group([('employee_id', 'in', self.ids),('clasification', '=', 'framework')], ['employee_id'], ['employee_id'])
        result = dict((data['employee_id'][0], data['employee_id_count']) for data in contract_data)
        for employee in self:
            employee.contracts_count = result.get(employee.id, 0)

class ClassificationDeductions(models.Model):
    _name = "hr_contract.classification_deductions"

    code = fields.Char(string='Code', size=4)
    name = fields.Char(string='Name')

    _sql_constraints = [
        ('name', 'unique (name)', 'The name must be unique!'),
        ('code', 'unique (code)', 'The code must be unique!')
    ]

class RetributionsDeductions(models.Model):
    _name = "hr_contract.retributions_deductions"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    amount = fields.Float(string="Amount")

    deduction_contract_ids = fields.Many2many('hr.contract',
                                    'retributions_deductions_contract_rel',
                                    string='Contract')

    type = fields.Selection(
        [('more', 'Contribution'), ('less', 'Deduction')], string='Type')

    classification_id = fields.Many2one('hr_contract.classification_deductions', string='Classification')

    show_in_contract = fields.Boolean(string='Show in contract', default=False)

    company_id = fields.Many2one('res.company', string='Company', readonly=True, copy=False,
                                 default=lambda self: self.env['res.company']._company_default_get(),
                                 )

    _sql_constraints = [
        ('name', 'unique (name)', 'The name must be unique!'),
        #('code', 'unique (code)', 'The code must be unique!')
    ]

    @api.one
    @api.constrains('amount','type')
    def _check_amount(self):
        if self.type == 'more':
            assert self.amount > 0, _('Amount must be greater than 0')
        if self.type == 'less':
            assert self.amount < 0, _('Amount must be smaller than 0')

    # @api.model
    # def create(self, vals):
    #
    #     line_code = vals.get('code', '_')
    #     line_code = re.sub('[^\w]', '', line_code.replace(' ', '_')).strip()
    #     vals.update({'code': line_code})
    #     num = 0
    #     while self.search_count([
    #         "|",
    #         ('code', '=', vals.get('code', '_')),
    #         ('name', '=', vals.get('name', '_'))
    #     ]):
    #         line_code = vals.get('code', '_')
    #         line_code = line_code.split("_")[0]
    #         line_code += "_" + str(num)
    #         line_name = vals.get('name', '_')
    #         line_name = line_name.split("_")[0]
    #         line_name += "_" + str(num)
    #         vals.update({'code': line_code, 'name': line_name})
    #         num += 1
    #
    #     return super(RetributionsDeductions, self).create(vals=vals)

    @api.multi
    def unlink(self):
        for move in self:
            if len(move.deduction_contract_ids):
                raise ValidationError(_('You can not delete a retribution/deduction in use'))

        return super(RetributionsDeductions, self).unlink()

class Job(models.Model):
    _inherit = "hr.job"

    counts_hired_employee = fields.Integer(compute='_compute_counts_hired_employees', store=True)
    contract_ids = fields.One2many('hr.contract', 'job_id', string='Contracts', groups='base.group_user')
    conditions_security_health = fields.Text('Conditions of security and health')
    code = fields.Char('Code')

    @api.depends('employee_ids.job_id')
    def _compute_counts_hired_employees(self):
        contract_data = self.env['hr.contract'].sudo().read_group([('job_id', 'in', self.ids),('clasification', '=','framework')], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in contract_data)
        for job in self:
            job.counts_hired_employee = result.get(job.id, 0)

# class ResourceCalendarAttendance(models.Model):
#     _inherit = "resource.calendar.attendance"
#
#     working_hours_shift = fields.Float(string='Working Hours of the shift',compute='_compute_working_hours_shift',store=True)
#
#     @api.depends('hour_from','hour_to','rest_time','calendar_id.rest_time')
#     def _compute_working_hours_shift(self):
#         for resource in self:
#             resource.working_hours_shift = (resource.hour_to - resource.hour_from)-resource.rest_time

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
