# -*- coding: utf-8 -*-
import base64
from StringIO import StringIO
from datetime import timedelta, datetime, date

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import ustr

resp_dic = {'nokey': _ ( 'You must request a registry key. Please contact the suport center for a new one.' ),
            'invalidkey': _ ( 'You are using a invalid key. Please contact the suport center for a new one.' ),
            'expkey': _ ( 'You are using a expired key. Please contact the suport center for a new one.' )}


class Judgment ( models.Model ):
    _name = "l10n_cu_contract.judgment"

    date_judgment = fields.Date ( 'Judgment Date', required=True )
    judgment = fields.Binary ( 'Judgment', required=True )
    judgment_file_name = fields.Char ( string='Judgment file name' )
    contract_id = fields.Many2one ( 'l10n_cu_contract.contract', 'Contract' )


class Reclamation ( models.Model ):
    _name = "l10n_cu_contract.reclamation"

    dateR = fields.Date ( "Date" )
    observation = fields.Char ( 'Observation' )
    contract_id = fields.Many2one ( comodel_name='l10n_cu_contract.contract', string='Contract' )


class ContractLines ( models.Model ):
    _name = 'l10n_cu_contract.contract_lines'
    _rec_name = 'product_id'

    @api.model
    def _get_company_currency(self):
        return self.env.user.company_id.currency_id

    contract_id = fields.Many2one ( 'l10n_cu_contract.contract', 'Contract', required=True, ondelete='cascade' )
    sequence = fields.Integer ( default=10, help="Gives the sequence of this line when displaying the invoice." )
    product_id = fields.Many2one ( 'product.product', 'Product', required=True )
    description = fields.Char ( 'Description', size=64, readonly=True, related='product_id.name' )
    quantity = fields.Float ( 'Quantity', default=0, required=True )
    quantity_invoice = fields.Float ( 'Invoice Quantity', compute='_quantity_invoice' )
    price = fields.Monetary ( 'Price', required=True)
    currency_id = fields.Many2one ( 'res.currency', default=_get_company_currency, string="Currency",
                                    help='Utility field to express amount currency' )
    amount = fields.Monetary ( 'Amount', compute='_amount_line' )
    amount_payment = fields.Monetary ( 'Amount Payment', readonly=True, compute='_compute_amount_payment' )
    payment_lines = fields.One2many ( 'l10n_cu_contract.lines_milestone_payment', 'contract_lines_ids',
                                      'Payment Lines' )
    account_analytic_id = fields.Many2one ( 'account.analytic.account', string='Analytic Account' )

    @api.one
    def _compute_amount_payment(self):
        amount_payment = 0
        if self.payment_lines:
            for payment in self.payment_lines:
                amount_payment += payment.amount_payment
        self.amount_payment = amount_payment

    @api.one
    def _quantity_invoice(self):
        qty = 0
        for invoice in self.contract_id.invoice_ids:
            if invoice.state in ['draft', 'open', 'paid']:
                for line in invoice.invoice_line_ids:
                    if line.product_id == self.product_id:
                        qty += line.quantity
        self.quantity_invoice = qty

    @api.onchange ( 'product_id' )
    def _onchange_product(self):
        if self.product_id:
            self.price = self.product_id.list_price

    @api.one
    @api.depends ( 'quantity', 'price' )
    def _amount_line(self):
        self.amount = self.price * self.quantity

    @api.depends ( 'product_id' )
    def _get_price(self):
        for c_model in self:
            if c_model.product_id:
                c_model.price = c_model.product_id.list_price

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        active = self._context.get ( 'active_id' )
        obj = self.env['l10n_cu_contract.contract'].search ( [('id', '=', active)] )
        recs = self.search ( [('contract_id', '=', obj.id)] + args, limit=limit )
        return recs.name_get ( )


class MilestonePayment ( models.Model ):
    _name = "l10n_cu_contract.milestone_payment"

    @api.model
    def _get_company_currency(self):
        return self.env.user.company_id.currency_id

    # TODO: check next line, duplicate column contract_id
    contract_id = fields.Many2one ( 'l10n_cu_contract.contract', 'Contract', required=True )
    contract_id = fields.Many2one ( 'l10n_cu_contract.contract', 'Contract', required=True, ondelete='cascade' )
    sequence = fields.Integer ( default=10, help="Gives the sequence of this line when displaying the invoice." )
    name = fields.Char ( 'Name' )
    date = fields.Date ( 'Date', required=True )
    line_ids = fields.Many2one ( 'l10n_cu_contract.line_milestone_payment', 'Product Lines', copy=False, required=True )
    notes = fields.Text ( 'Notes' )


class LineMilestonePayment ( models.Model ):
    _name = "l10n_cu_contract.line_milestone_payment"

    @api.model
    def _get_active_id(self):
        if self._context.get ( 'active_id' ):
            return self._context.get ( 'active_id' )

    name = fields.Char ( string='Name', compute='_compute_name', invisible=True )
    lines_milestone_payment = fields.One2many ( 'l10n_cu_contract.lines_milestone_payment', 'line_milestone_payment_id',
                                                'Lines Milestone Payment' )
    active_id = fields.Char ( 'Active', default=_get_active_id )

    @api.one
    def _compute_name(self):
        for record in self:
            if record.lines_milestone_payment:
                record.name = str ( record.lines_milestone_payment[0].description ) + ' ' + str (
                    record.lines_milestone_payment[0].amount_payment )


class LinesMilestonePayment ( models.Model ):
    _name = "l10n_cu_contract.lines_milestone_payment"

    @api.model
    def _get_company_currency(self):
        return self.env.user.company_id.currency_id

    contract_lines_ids = fields.Many2one ( 'l10n_cu_contract.contract_lines', string="Contract Lines", copy=False,
                                           required=True )
    description = fields.Char ( related='contract_lines_ids.description' )
    currency_id = fields.Many2one ( 'res.currency', default=_get_company_currency, readonly=True, string="Currency",
                                    help='Utility field to express amount currency' )
    amount = fields.Monetary ( related='contract_lines_ids.amount' )
    amount_payment_contract_line = fields.Monetary ( related='contract_lines_ids.amount_payment' )
    amount_payment = fields.Monetary ( 'Amount', required=True )
    line_milestone_payment_id = fields.Many2one ( 'l10n_cu_contract.line_milestone_payment', 'Line Milestone Payment' )

    @api.onchange ( 'contract_lines_ids' )
    def _onchange_contract_lines(self):
        self.amount_payment = self.contract_lines_ids.amount - self.contract_lines_ids.amount_payment


class Contract ( models.Model ):
    _name = "l10n_cu_contract.contract"
    _inherit = ['mail.thread']
    _order = 'create_date desc, date_end desc, number desc'

    @api.model
    def _get_employee(self):
        employee_ids = self.env['hr.employee'].search ( [('user_id', '=', self.env.user.id)] )
        if employee_ids:
            return employee_ids
        else:
            return False

    @api.model
    def _get_company_currency(self):
        return self.env.user.company_id.currency_id

    @api.model
    def _default_year(self):
        fecha = date.today ( )
        fecha_list = str ( fecha ).split ( '-' )
        return fecha_list[0]

    def default_year(self):
        fecha = str ( date.today ( ) ).split ( '-' )
        year_list = []
        for i in range ( int ( fecha[0] ) - 5, int ( fecha[0] ) + 5 ):
            tuple = (str ( i ), str ( i ))
            year_list.append ( tuple )
        return year_list

    # @api.model
    # def _default_internal_number_contract(self):
    #     if self.env.context.get('flow') == 'customer':
    #         sequence = self.env['ir.sequence'].search([('code', '=', 'contract.internal.number')])
    #         return sequence.get_next_char(sequence.number_next_actual)
    #     else:
    #         return False

    name = fields.Char ( 'Name', required=True, readonly=True, states={'draft': [('readonly', False)]},
                         help='Object of the contract', size=100 )
    number_archive_partner = fields.Char ( 'Number of Archive', related='partner_id.archive_nro' )
    number = fields.Char ( 'Number',
                           help='In case the contract type has a sequence associated the number will be automatically generated',
                           track_visibility='onchange', readonly=True)
    complete_number = fields.Char ( 'Number', compute='_compute_complete_number' )
    internal_number_contract = fields.Char ( 'Internal number', help='Número interno del contrato')

    judgment_ids = fields.One2many ( 'l10n_cu_contract.judgment', 'contract_id', 'Judgment',
                                     track_visibility='onchange' )

    date_start = fields.Date ( 'Start Date', help='Initial date of the contract', track_visibility='onchange' )
    date_end = fields.Date ( 'End Date', help='End date of the contract', track_visibility='onchange' )
    date_send_signed = fields.Date ( 'Date Send Signed', help='Date sent to sign the contract by the client',
                                     track_visibility='onchange' )
    partner_id = fields.Many2one ( 'res.partner', 'Partner', required=True, track_visibility='onchange', )
    dst = fields.Selection([('si', 'SI'), ('no', 'NO')], 'DST', required=True)
    tcp = fields.Selection([('si', 'SI'), ('no', 'NO')], 'TCP', required=True)
    state = fields.Selection (
        [('draft', 'New'), ('pending_dict', 'Pending Dict.'), ('pending_appro', 'Pending Appro.'),
         ('rejected', 'Rejected'), ('approval', 'Approved'), ('pending_signed', 'Pending Signed'),
         ('open', 'In Action'), ('close', 'Closed'), ('cancelled', 'Cancelled')], 'Status', required=True,
        track_visibility='onchange', default='draft' )
    validity_date_progress = fields.Float ( 'Validity date progress', compute='_validity_date_progress',
                                            help='Visual element that represents the remaining percent of validity in the contract' )
    days = fields.Float ( 'Days', compute='_compute_days' )
    contract_type = fields.Many2one ( 'l10n_cu_contract.contract_type', 'Contract Type', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]} )
    parent_id = fields.Many2one ( 'l10n_cu_contract.contract', 'Parent', readonly=True,
                                  states={'draft': [('readonly', False)]}, track_visibility='onchange' )
    company_id = fields.Many2one ( 'res.company', 'Company', track_visibility='onchange' )
    line_ids = fields.One2many ( 'l10n_cu_contract.contract_lines', 'contract_id', 'Lines',
                                 track_visibility='onchange' )
    employee_id = fields.Many2one ( 'hr.employee', 'User', readonly=True, default=_get_employee )
    related_employee_id = fields.Many2one ( 'hr.employee', 'Related Employee',
                                            help='Employee in charge of following up the contract',
                                            track_visibility='onchange' )
    responsible_employee_id = fields.Many2one('hr.employee', 'Responsible Employee', track_visibility='onchange')
    department_responsible_employee_id = fields.Many2one('hr.department', 'Department', track_visibility='onchange')

    note = fields.Text ( 'Notes' )
    milestone_payment_ids = fields.One2many ( 'l10n_cu_contract.milestone_payment', 'contract_id', 'Milestone Payments',
                                              ondelete='cascade', track_visibility='onchange' )
    currency_id = fields.Many2one ( 'res.currency', default=_get_company_currency, readonly=True, string="Currency",
                                    help='Utility field to express amount currency' )
    amount_total = fields.Monetary ( 'Amount Total', compute='_amount_total', store=True )
    amount_invoice = fields.Monetary ( 'Amount Invoice', compute='_amount_invoice', store=True )
    amount_rest = fields.Monetary ( 'Amount Rest', compute='_amount_rest', store=True )
    invoice_ids = fields.One2many ( 'account.invoice', 'contract_id', 'Invoice' )
    number_readonly = fields.Boolean ( compute='_compute_number' )
    flow = fields.Selection ( [('customer', 'Sale'), ('supplier', 'Purchase'), ], 'Flow', required=True )
    company_id = fields.Many2one ( 'res.company', string='Company', readonly=True,
                                   default=lambda self: self.env.user.company_id )
    update_date = fields.Boolean ( 'Update Date', default=False, help="Update end date of parent contract" )
    update_lines = fields.Boolean ( 'Update Lines', default=False, help="Update lines of parent contract" )
    option_select = fields.Selection ( [('add', 'Add new'), ('update_quantity', 'Update Quantity'), ], )
    department_id = fields.Many2one ( 'hr.department', 'Department Related Employee', track_visibility='onchange' )
    property_payment_term_id = fields.Many2one ( 'account.payment.term', company_dependent=True,
                                                 string='Payment Terms' )
    payment_method_id = fields.Many2one ( 'account.payment.method', 'Método de pago' )
    child_ids = fields.One2many ( 'l10n_cu_contract.contract', 'parent_id', 'Childs' )
    hco = fields.Boolean ( 'HCO', default=False, help="Until the fulfillment of the obligations" )
    amount_bool = fields.Boolean ( 'Amount Open', default=False, help="" )
    municipality_id = fields.Many2one ( 'l10n_cu_base.municipality', 'Municipality' )

    # date_claim = fields.Date('Date claim')
    # observation = fields.Text('Observation')

    revision = fields.Boolean ( 'Review at the beginning of the year' )
    year = fields.Selection ( default_year, string='Revision year', default=_default_year )
    # TODO:campos para los comites de contratacion
    committee_ids = fields.Many2many ( 'l10n_cu_contract.contract_committee', 'contract_committee_rel', 'contract_id',
                                       'committee_id', 'Committee', compute='_compute_committee', readonly=True,
                                       track_visibility='onchange' )
    committee = fields.Boolean ( 'Committee', compute='_compute_committee' )
    # TODO:campos relacionales para el funcionamiento (tipos de contratos)
    required_parent = fields.Boolean ( related='contract_type.required_parent' )
    required_judgment = fields.Boolean ( related='contract_type.required_judgment' )
    required_lines = fields.Boolean ( related='contract_type.required_lines' )
    required_milestone_payment = fields.Boolean ( related='contract_type.required_milestone_payment' )
    required_parent_id = fields.Many2one ( related='contract_type.parent_id' )
    # TODO:campos relacionales para el funcionamiento de la vista pivot
    reeup_code = fields.Char ( related='partner_id.reeup_code', string='Reeup Code', store=True )
    state_id = fields.Char ( related='partner_id.state_id.name', string='State', store=True )
    product = fields.Char ( related='line_ids.product_id.name', string='Product', store=True )
    ministry = fields.Char ( related='partner_id.ministry_id.name', string='Ministry', store=True )
    quantity = fields.Float ( related='line_ids.quantity', string='Quantity', store=True )
    quantity_invoice = fields.Float ( related='line_ids.quantity_invoice', string='Quantity', store=True )
    percentage_execution = fields.Float ( '% Monetary Execution', compute='_compute_percentage_execution', store=True,
                                          help='Visual element that represents the percent of monetary execution' )

    reclamation_ids = fields.One2many ( comodel_name='l10n_cu_contract.reclamation', inverse_name='contract_id',
                                        string='Reclamation' )

    sql_constraints = [('number_type_uniq', 'unique (number, contract_type)',
                        'The number and the contract type combination must be unique'),
                       ('number_uniq', 'unique(number)', 'The number must be unique!'), ]

    @api.onchange ( 'hco' )
    def onchange_hco(self):
        if self.hco:
            self.date_end = False

    @api.onchange ( 'partner_id' )
    def onchange_partner_id(self):
        if self.partner_id and self.partner_id.municipality_id:
            self.municipality_id = self.partner_id.municipality_id.id

    @api.onchange ( 'related_employee_id' )
    def onchange_related_employee_id(self):
        if self.related_employee_id and self.related_employee_id.department_id:
            self.department_id = self.related_employee_id.department_id.id

    @api.onchange ( 'option_select', 'partner_id' )
    def onchange_option_select(self):
        if self.option_select and self.option_select == 'update_quantity':
            if not self.parent_id:
                self.option_select = ''
                raise UserError ( _ ( "I need select the parent contract!" ) )
            self.line_ids = [(5, 0, 0)]
            array = []
            for line in self.parent_id.line_ids:
                dicc = {}
                dicc['contract_id'] = self.id
                dicc['price'] = line.price
                dicc['quantity'] = line.quantity
                dicc['currency_id'] = line.currency_id.id
                dicc['product_id'] = line.product_id.id
                array.append ( (0, 0, dicc) )
            self.line_ids = array
        elif self.option_select and self.option_select == 'new':
            self.line_ids = [(5, 0, 0)]

    @api.multi
    def _compute_complete_number(self):
        for record in self:
            number = record.number
            if record.parent_id.number:
                if number:
                    number = number + ' al ' + record.parent_id.number
            record.complete_number = number

    @api.one
    @api.depends ( 'date_end' )
    def _compute_days(self):
        if self.date_end:
            date_end = datetime.strptime ( self.date_end, '%Y-%m-%d' )
            today = datetime.today ( )
            self.days = (date_end - today).days

    @api.constrains ( 'date_start', 'date_end' )
    def _check_dates(self):
        if self.date_start and self.date_end:
            if self.date_end < self.date_start and not self.hco:
                raise ValidationError ( _ ( 'Error! End date must be greater than start date.' ) )

    @api.constrains ( 'date_start', 'date_end', 'date_send_signed' )
    def _check_dates_sign(self):
        if self.date_start and self.date_send_signed:
            if self.date_send_signed > self.date_start:
                raise ValidationError ( _ ( 'Error! Date start must be greater than signed date.' ) )

    def _get_attr_value(self, attr):
        if attr == 'state':
            if self.state == 'draft':
                return _ ( 'New' )
            elif self.state == 'pending_dict':
                return _ ( 'Pending Dict.' )
            elif self.state == 'pending_appro':
                return _ ( 'Pending Appro.' )
            elif self.state == 'rejected':
                return _ ( 'Rejected' )
            elif self.state == 'approval':
                return _ ( 'Approved' )
            elif self.state == 'pending_signed':
                return _ ( 'Pending Signed' )
            elif self.state == 'open':
                return _ ( 'In Progress' )
            elif self.state == 'close':
                return _ ( 'Closed' )
            elif self.state == 'cancelled':
                return _ ( 'Cancelled' )

        elif attr == 'contract_type':
            return self.contract_type.name or ''

        elif attr == 'related_employee_id':
            return self.related_employee_id.name or ''

        elif attr == 'partner_name':
            return self.partner_id.name or ''

        elif attr == 'partner_reeup_code':
            return self.partner_id.reeup_code or ''

        val = getattr ( self, attr, False )
        return val or ''

    @api.one
    def _compute_committee(self):
        a = self.env['l10n_cu_contract.line_contract'].search ( [('contract_id', '=', self.id)] )
        array = []
        for b in a:
            array.append ( b.contract_committee_id.id )
        self.committee_ids = array
        if len ( array ) > 0:
            self.committee = True
        else:
            self.committee = False

    @api.one
    @api.depends ( 'contract_type' )
    def _compute_number(self):
        if self.contract_type and (self.contract_type.sequence_id or self.contract_type.parent_consecutive):
            self.number_readonly = True
        else:
            self.number_readonly = False

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.number:
                name = record.number + '/' + name + '/' + str ( record.amount_rest )
            else:
                name = record.name + '/' + str ( record.amount_rest )
            res.append ( (record.id, name) )
        return res

    @api.one
    @api.depends('line_ids')
    def _amount_total(self):
        total = 0
        for line in self.line_ids:
            total += line.amount
        self.amount_total = total

    @api.one
    @api.depends('invoice_ids')
    def _amount_invoice(self):
        total = 0
        for invoice in self.invoice_ids:
            if invoice.state != 'cancel':
                total += invoice.amount_total
        for contract in self.child_ids:
            if contract.update_lines:
                total += contract.amount_invoice
        self.amount_invoice = total

    @api.one
    @api.depends('amount_total', 'amount_invoice', 'amount_bool')
    def _amount_rest(self):
        if not self.amount_bool:
            self.amount_rest = self.amount_total - self.amount_invoice
        else:
            self.amount_rest = 0

    @api.one
    @api.depends ( 'date_start', 'date_end' )
    def _validity_date_progress(self):
        if self.date_start and self.date_end:
            date_start = datetime.strptime ( self.date_start, '%Y-%m-%d' )
            date_end = datetime.strptime ( self.date_end, '%Y-%m-%d' )
            today = datetime.today ( )
            total_days = date_end - date_start
            init_date = today
            if today < date_start:
                init_date = date_start
            current_days = (date_end - init_date).days

            if current_days < 0:
                self.validity_date_progress = 0
            if total_days.days == 0:
                self.validity_date_progress = 0
            else:
                self.validity_date_progress = current_days * 100 / total_days.days

    @api.depends ( 'amount_total', 'amount_invoice' )
    def _compute_percentage_execution(self):
        for contract in self:
            if contract.amount_total and contract.amount_invoice:
                if contract.amount_total != 0:
                    percentage = (contract.amount_invoice / contract.amount_total) * 100.00
                    contract.percentage_execution = percentage
                else:
                    contract.percentage_execution = 0
            else:
                contract.percentage_execution = 0

    @api.onchange ( 'parent_id' )
    def _onchange_parent(self):
        if self.parent_id:
            self.partner_id = self.parent_id.partner_id.id

    @api.model
    def create(self, vals):
        if vals.get ( 'parent_id' ):
            parent = self.browse ( vals['parent_id'] )
            vals.update ( {'partner_id': parent.partner_id.id} )

        res = super ( Contract, self ).create ( vals )

        if res.required_parent and res.number_readonly and res.parent_id:
            ids = self.search ( [('parent_id', '=', res.parent_id.id)] )
            res.write ( {'number': int ( len ( ids ) )} )

        if res.contract_type.sequence_id.name == 'Desoft Holguin':
            number = res.contract_type.sequence_id.next_by_id ( )
            code = res.municipality_id.code
            if code:
                if len ( code ) < 2:
                    code = '0' + str ( code )
            else:
                code = '00'
            number_complete = '32' + code + str ( number )
            res.write ( {'number': number_complete} )

        number_sequence = res.partner_id.get_next_contract_number()
        year = date.today().year
        if res.flow == 'customer':
            # internal_number_sequence = self.env['ir.sequence'].next_by_code('contract.internal.number') or '/'
            internal_number_sequence = res.contract_type.get_next_contract_type_number()
            res.write({'internal_number_contract': internal_number_sequence})
            number = "{}-{}-V".format(res.number_archive_partner, number_sequence)
            res.write({'number': number})
        if res.flow == 'supplier':
            number = "{}-{}-P".format(res.number_archive_partner, number_sequence)
            res.write({'number': number})
        return res

    @api.one
    def set_pending_dict(self):
        if self.required_lines:
            if not self.line_ids:
                raise UserError ( _ ( "I need some detail lines!" ) )

        # # Equipo de venta
        # sales_team = self.env['crm.team'].search([('type', '=', 'sale'), ('legal', '=', True)])
        # email_to = ''
        # for sale in sales_team:
        #     for member in sale.member_ids:
        #         if member.partner_id.email:
        #             email_to += member.partner_id.email + ','
        # dicc = {
        #     'email_to': email_to
        # }
        # template = self.env.ref('l10n_cu_hlg_contract.mail_template_data_notification_email_contract')
        # contract_array = []
        # contract_array.append((self.number, self.partner_id.name, self.name))
        #
        # template.with_context(dbname=self._cr.dbname, contract=contract_array).send_mail(self.id, force_send=True,
        #                                                                                  email_values=dicc)


        self.state = 'pending_dict'

    @api.one
    def set_draft(self):
        self.state = 'draft'
        sales = self.env['sale.order'].search ( [('contract_id', '=', self.id)] )
        sales.unlink ( )

    @api.one
    def set_close(self):
        if self.child_ids:
            ban = False
            for contract in self.child_ids:
                if contract.state not in ['cancelled', 'close']:
                    ban = True
            if ban:
                raise UserError ( _ ( "You can not close a contract with children without closing!" ) )
        self.state = 'close'

    @api.one
    def set_pending_approv(self):
        if not self.judgment_ids and self.required_judgment:
            raise UserError ( _ ( "I need some judgment lines!" ) )
        self.state = 'pending_appro'

    @api.one
    def set_approval(self):
        if not self.date_send_signed:
            self.date_send_signed = fields.Datetime.now ( )
        self.state = 'approval'

    @api.one
    def set_rejected(self):
        self.state = 'rejected'

    @api.one
    def set_new(self):
        self.state = 'draft'

    @api.one
    def set_cancel(self):
        self.state = 'cancelled'

    @api.one
    def set_pending_signed(self):
        if not self.date_send_signed:
            self.date_send_signed = fields.Datetime.now ( )
        if not self.date_start:
            self.date_start = fields.Datetime.now ( )
        year = timedelta ( days=(self.contract_type.term * 365) )
        if not self.date_end and not self.hco:
            self.date_end = datetime.strptime ( self.date_start, '%Y-%m-%d' ) + year
        if self.required_lines:
            if not self.line_ids:
                raise UserError ( _ ( "I need some detail lines!" ) )

        # generate the number
        if self.contract_type.sequence_id and not self.contract_type.sequence_id.name == 'Desoft Holguin':
            self.number = self.contract_type.sequence_id.next_by_id ( )
        self.state = 'pending_signed'

    @api.one
    def set_open(self):
        if not self.number:
            raise UserError ( _ ( "Error! Number in contract empty." ) )
        contract_initial = self.env['ir.config_parameter'].sudo ( ).get_param ( 'contract_initial' )
        if contract_initial == 'False':
            if self.date_end < fields.Datetime.now ( ) and not self.hco:
                raise UserError ( _ ( "Error! End date must be greater than actual date." ) )
        if self.update_date:
            self.parent_id.date_end = self.date_end
        if self.update_lines:
            if self.option_select == 'add':
                array = []
                for line in self.line_ids:
                    dicc = {}
                    dicc['contract_id'] = self.parent_id.id
                    dicc['price'] = line.price
                    dicc['quantity'] = line.quantity
                    dicc['currency_id'] = line.currency_id.id
                    dicc['product_id'] = line.product_id.id
                    array.append ( (0, 0, dicc) )
                self.parent_id.line_ids = array
            elif self.option_select == 'update_quantity':
                array = []
                self.parent_id.line_ids = [(5, 0, 0)]
                for line in self.line_ids:
                    dicc = {}
                    dicc['contract_id'] = self.parent_id.id
                    dicc['price'] = line.price
                    dicc['quantity'] = line.quantity
                    dicc['currency_id'] = line.currency_id.id
                    dicc['product_id'] = line.product_id.id
                    array.append ( (0, 0, dicc) )
                self.parent_id.line_ids = array

        if self.required_milestone_payment:
            if not self.milestone_payment_ids:
                raise UserError ( _ ( "I need some milestone payments!" ) )
            else:
                sale_order_obj = self.env['sale.order']
                for payment in self.milestone_payment_ids:
                    array = []
                    for line in payment.line_ids.lines_milestone_payment:
                        quantity = line.amount_payment / line.contract_lines_ids.price
                        data_sale_order_line = dict ( name=line.contract_lines_ids.product_id.name,
                                                      invoice_status='to invoice',
                                                      product_id=line.contract_lines_ids.product_id.id,
                                                      price_unit=line.contract_lines_ids.price,
                                                      product_uom_qty=quantity,
                                                      product_uom=line.contract_lines_ids.product_id.uom_id.id, )
                        array.append ( (0, 0, data_sale_order_line) )
                    data_sale_order = dict ( partner_id=self.partner_id.id, partner_invoice_id=self.partner_id.id,
                                             partner_shipping_id=self.partner_id.id,
                                             pricelist_id=self.env.ref ( 'product.list0' ).id, order_line=array,
                                             origin=self.number, contract_id=self.id, external_create=True,
                                             date_order=payment.date, user_id=self.employee_id.user_id.id,
                                             department_id=self.department_id.id, )
                    sale_order_obj.create ( data_sale_order )

        if not self.parent_id:
            contract = self.search ( [('number', '=', self.number), ('contract_type', '=', self.contract_type.id)] )
        else:
            contract = self.search ( [('number', '=', self.number), ('parent_id', '=', self.parent_id.id)] )

        if len ( contract ) > 1:
            raise UserError ( _ ( "Error! The numbers of contracts can not be the same." ) )

        self.state = 'open'

    @api.one
    def set_open2(self):
        self.state = 'open'

    @api.one
    def clear_milestone(self):
        lines_milestone_obj = self.env['l10n_cu_contract.lines_milestone_payment']
        lines_ids = lines_milestone_obj.search ( [('contract_lines_ids', 'in', self.line_ids.ids)] )
        lines_ids.unlink ( )

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state != 'draft':
                raise UserError ( _ ( "Unlink in state draft." ) )
            if obj.child_ids:
                raise UserError ( _ ( "You can not delete contracts with related specifics." ) )
            if obj.invoice_ids:
                raise UserError ( _ ( "You can not delete contracts with related invoices." ) )

        return super ( Contract, self ).unlink ( )

    @api.constrains ( 'milestone_payment_ids' )
    def _check_milestone_payment(self):
        if self.milestone_payment_ids:
            total_mp = 0
            for mp in self.milestone_payment_ids:
                for line in mp.line_ids.lines_milestone_payment:
                    total_mp += line.amount_payment
            if round ( total_mp, 2 ) != round ( self.amount_total, 2 ):
                raise ValidationError ( _ ( 'Error! Milestone Payment is wrong.' ) )

    @api.onchange ( 'date_start' )
    def onchange_date_start(self):
        if self.date_start:
            year = timedelta ( days=(self.contract_type.term * 365) )
            self.date_end = datetime.strptime ( self.date_start, '%Y-%m-%d' ) + year

    @api.multi
    def print_contract(self):
        for contract in self:
            if not contract.contract_type.template_data:
                self.env.user.notify_info ( 'You must have a template configured.' )
            else:
                cta_ban_cup = self.env['res.partner.bank'].search (
                    [('partner_id', '=', contract.partner_id.id), ('currency_id', '=', 'CUP')], limit=1 )
                cta_ban_cuc = self.env['res.partner.bank'].search (
                    [('partner_id', '=', contract.partner_id.id), ('currency_id', '=', 'CUC')], limit=1 )
                list_product = []
                if len ( contract.line_ids ) != 0:
                    for line in contract.line_ids:
                        product = {}
                        product['name'] = line.product_id.name
                        product['quantity'] = line.quantity
                        product['price'] = str ( line.price ) + " " + str ( line.currency_id.name )
                        product['amount'] = str ( line.amount ) + " " + str ( line.currency_id.name )
                        product['currency'] = line.currency_id.name
                        list_product.append ( product )
                datas = {'ids': [contract.id], 'name': contract.partner_id.name,
                         'short_name': contract.partner_id.short_name,
                         'acc_res_no_boss': contract.partner_id.acc_res_no_boss,
                         'acc_res_date_boss': contract.partner_id.acc_res_date_boss,
                         'acc_res_emitted_boss': contract.partner_id.acc_res_emitted_boss,
                         'acc_res_name_boss': contract.partner_id.acc_res_name_boss,
                         'acc_res_position_boss': contract.partner_id.acc_res_position_boss,
                         'reeup': contract.partner_id.reeup_code, 'nit': contract.partner_id.nit_code,
                         'email': contract.partner_id.email, 'phone': contract.partner_id.phone,
                         'street': contract.partner_id.street, 'municipality': contract.partner_id.municipality_id.name,
                         'state': contract.partner_id.state_id.name, 'c_bank_cup': cta_ban_cup.acc_number,
                         'titular_cup': cta_ban_cup.name, 'bank_name_cup': cta_ban_cup.bank_id.name,
                         'bank_code_cup': cta_ban_cup.bank_id.bic, 'bank_phone_cup': cta_ban_cup.bank_id.phone,
                         'bank_street_cup': cta_ban_cup.bank_id.street, 'bank_email_cup': cta_ban_cup.bank_id.email,
                         'c_bank_cuc': cta_ban_cuc.acc_number, 'titular_cuc': cta_ban_cuc.name,
                         'bank_name_cuc': cta_ban_cuc.bank_id.name, 'bank_code_cuc': cta_ban_cuc.bank_id.bic,
                         'bank_phone_cuc': cta_ban_cuc.bank_id.phone, 'bank_street_cuc': cta_ban_cuc.bank_id.street,
                         'bank_email_cuc': cta_ban_cuc.bank_id.email, 'ministry': contract.partner_id.ministry_id.name,
                         'list_product': list_product, 'usd_license_number': contract.partner_id.usd_license_number,
                         'amount_total': contract.amount_total,'mercantil_register':contract.partner_id.mercantil_register,
                         'code_swift':contract.partner_id.code_swift}
                res = {'type': 'ir.actions.report.xml',
                       'report_name': contract.contract_type.ir_actions_report_xml_id.report_name, 'datas': datas,}
                return res

    @api.model
    def send_email_contract(self):
        days = int ( self.env['ir.config_parameter'].sudo ( ).get_param ( 'contract_days' ) )
        if not days:
            days = 30

        # Equipo de venta
        sales_team = self.env['crm.team'].search ( [('type', '=', 'sale')] )
        email_to = ''
        for sale in sales_team:
            for member in sale.member_ids:
                if member.partner_id.email:
                    email_to += member.partner_id.email + ','
        dicc = {'email_to': email_to}

        # para los contratos cercanos a la fecha de vencimiento
        template = self.env.ref ( 'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_test' )
        contract_array = []
        contracts = self.env['l10n_cu_contract.contract'].search (
            [('flow', '=', 'customer'), ('state', 'in', ['open'])], order='date_end asc' )
        for contract in contracts:
            if contract.date_end:
                time_validez = datetime.strptime ( contract.date_end, '%Y-%m-%d' ) - datetime.today ( )
                if time_validez.days >= 0:
                    if time_validez.days <= days:
                        contract_array.append ( (contract.number, contract.partner_id.name, contract.date_start,
                                                 contract.date_end, time_validez.days, contract.employee_id.name,
                                                 contract.department_id.name) )

        if len ( contract_array ) > 0:
            template.with_context ( dbname=self._cr.dbname, contract=contract_array ).send_mail ( self.id,
                                                                                                  force_send=True,
                                                                                                  email_values=dicc )

        # para los contratos que aun no han regresado del cliente
        template = self.env.ref (
            'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_send_signed_test' )
        contract_signed = []
        contracts = self.env['l10n_cu_contract.contract'].search (
            [('flow', '=', 'customer'), ('state', 'in', ['pending_signed'])], order='date_send_signed asc' )
        for contract in contracts:
            if contract.date_send_signed:
                time_validez = datetime.today ( ) - datetime.strptime ( contract.date_send_signed, '%Y-%m-%d' )
                contract_signed.append ( (contract.number, contract.partner_id.name, contract.date_send_signed,
                                          time_validez.days, contract.employee_id.name) )

        if len ( contract_signed ) > 0:
            template.with_context ( dbname=self._cr.dbname, contract_signed=contract_signed ).send_mail ( self.id,
                                                                                                          force_send=True,
                                                                                                          email_values=dicc )
        # para los contratos que estan cercanos a ejecutar el presupuesto completo
        percentage = self.env['ir.config_parameter'].sudo ( ).get_param ( 'contract_monetary' )
        if not percentage:
            percentage = 75
        template = self.env.ref ( 'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_monetary' )
        contract_monetary = []
        contracts = self.env['l10n_cu_contract.contract'].search (
            [('flow', '=', 'customer'), ('state', 'in', ['open'])], order='percentage_execution asc' )
        for contract in contracts:
            if contract.percentage_execution >= percentage:
                contract_monetary.append ( (contract.number, contract.partner_id.name, contract.name,
                                            contract.date_start, contract.date_end, contract.amount_total,
                                            contract.amount_invoice, contract.percentage_execution) )
        if len ( contract_monetary ) > 0:
            template.with_context ( dbname=self._cr.dbname, contract_monetary=contract_monetary ).send_mail ( self.id,
                                                                                                              force_send=True,
                                                                                                              email_values=dicc )

        # Equipo de compra
        purchase_team = self.env['crm.team'].search ( [('type', '=', 'purchase')] )
        email_to = ''
        for purchase in purchase_team:
            for member in purchase.member_ids:
                if member.partner_id.email:
                    email_to += member.partner_id.email + ','
        dicc = {'email_to': email_to}

        # para los contratos cercanos a la fecha de vencimiento
        template = self.env.ref ( 'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_test' )
        contract_array = []
        contracts = self.env['l10n_cu_contract.contract'].search (
            [('flow', '=', 'supplier'), ('state', 'in', ['open'])], order='date_end asc' )
        for contract in contracts:
            if contract.date_end:
                time_validez = datetime.strptime ( contract.date_end, '%Y-%m-%d' ) - datetime.today ( )
                if time_validez.days >= 0:
                    if time_validez.days <= days:
                        contract_array.append ( (contract.number, contract.partner_id.name, contract.date_start,
                                                 contract.date_end, time_validez.days, contract.employee_id.name,
                                                 contract.department_id.name) )

        if len ( contract_array ) > 0:
            template.with_context ( dbname=self._cr.dbname, contract=contract_array ).send_mail ( self.id,
                                                                                                  force_send=True,
                                                                                                  email_values=dicc )

        # para los contratos que aun no han regresado del cliente
        template = self.env.ref (
            'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_send_signed_test' )
        contract_signed = []
        contracts = self.env['l10n_cu_contract.contract'].search (
            [('flow', '=', 'supplier'), ('state', 'in', ['pending_signed'])], order='date_send_signed asc' )
        for contract in contracts:
            if contract.date_send_signed:
                time_validez = datetime.today ( ) - datetime.strptime ( contract.date_send_signed, '%Y-%m-%d' )
                contract_signed.append ( (contract.number, contract.partner_id.name, contract.date_send_signed,
                                          time_validez.days, contract.employee_id.name) )

        if len ( contract_signed ) > 0:
            template.with_context ( dbname=self._cr.dbname, contract_signed=contract_signed ).send_mail ( self.id,
                                                                                                          force_send=True,
                                                                                                          email_values=dicc )

            # para los contratos que estan cercanos a ejecutar el presupuesto completo
            percentage = int ( self.env['ir.config_parameter'].sudo ( ).get_param ( 'contract_monetary' ) )
            if not percentage:
                percentage = 75
            template = self.env.ref ( 'l10n_cu_hlg_contract.mail_template_data_notification_email_contract_monetary' )
            contract_monetary = []
            contracts = self.env['l10n_cu_contract.contract'].search (
                [('flow', '=', 'customer'), ('state', 'in', ['open'])], order='percentage_execution asc' )
            for contract in contracts:
                if contract.percentage_execution >= percentage:
                    contract_monetary.append ( (contract.number, contract.partner_id.name, contract.name,
                                                contract.date_start, contract.date_end, contract.amount_total,
                                                contract.amount_invoice, contract.percentage_execution) )
            if len ( contract_monetary ) > 0:
                template.with_context ( dbname=self._cr.dbname, contract_monetary=contract_monetary ).send_mail (
                    self.id, force_send=True, email_values=dicc )

        # Para cerrar los contratos
        contracts = self.env['l10n_cu_contract.contract'].search ( [('state', 'not in', ['close', 'cancelled'])] )
        for cont in contracts:
            if not cont.hco:
                if cont.days <= 0:
                    cont.state = 'close'

        return True

    @api.one
    @api.constrains ( 'name' )
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg ( 'l10n_cu_contract' )
        if resp != 'ok':
            raise ValidationError ( resp_dic[resp] )
