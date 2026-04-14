# -*- coding: utf-8 -*-
from datetime import datetime, date
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

import babel
import pytz

resp_dic = {'nokey': _('You must request a registry key. Please contact the suport center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the suport center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the suport center for a new one.')}


class ContractAgreement(models.Model):
    _name = "l10n_cu_contract.contract_agreement"

    name = fields.Char(string='Name', compute='_compute_name')
    number = fields.Char('Number', required=True, copy=False)
    manager_id = fields.Many2one('hr.employee', 'Manager', required=True, copy=False)
    date = fields.Date('Date of fulfillment', required=True, copy=False)

    @api.one
    def _compute_name(self):
        for record in self:
            record.name = str(record.number)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = [('id', '=', 0)]
        obj = self.search(domain + args, limit=0)
        return obj.name_get()


class LineContract(models.Model):
    _name = "l10n_cu_contract.line_contract"

    contract_id = fields.Many2one('l10n_cu_contract.contract', 'Contract', required=True)
    contract_agreement_ids = fields.Many2many('l10n_cu_contract.contract_agreement', 'contract_agreement_rel',
                                              string='Contract Agreement')
    contract_committee_id = fields.Many2one('l10n_cu_contract.contract_committee', 'Contract Committee')

#points for meeting reunion
class CommiteePoint(models.Model):
    _name = "l10n_cu_contract.meeting_point"

    subject = fields.Char(string='Asunto')
    contract_committee_id = fields.Many2one('l10n_cu_contract.contract_committee',string='Comité de Contratación',readonly=True)
#class for agreements


class ContractCommittee(models.Model):
    _name = "l10n_cu_contract.contract_committee"
    _inherit = ['mail.thread']
    _rec_name = 'nro_committee'

    nro_committee = fields.Char('Committee Nro', required=True, track_visibility='always',
                                states={'draft': [('readonly', False)]})
    date_committee = fields.Date('Committee Date', default= datetime.today(),required=True, track_visibility='always',
                                 states={'draft': [('readonly', False)]})
    manager_id = fields.Many2one('hr.employee','Manager', required=True, track_visibility='always',
                                 states={'draft': [('readonly', False)]})
    template = fields.Binary(string='Contract Committee File', states={'draft': [('readonly', False)]})
    template_file_name = fields.Char(string='Template file name', states={'draft': [('readonly', False)]})
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_contract_committee_rel', 'employee_id',
                                    'contract_committee_id', 'Employee', track_visibility='always',
                                    states={'draft': [('readonly', False)]})
    line_contract_ids = fields.One2many('l10n_cu_contract.line_contract', 'contract_committee_id', 'Contract',
                                        states={'draft': [('readonly', False)]}, track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id.id, states={'draft': [('readonly', False)]})
    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)
    state = fields.Selection([('draft', 'New'),
                              ('open', 'In Action'),
                              ],
                             'Status', required=True,
                             track_visibility='onchange', default='draft')

    #campos agregados a este modelo
    assistans_ids = fields.Many2many('hr.employee', 'hr_employee_contract_committee_rel', 'employee_id',
                                    'contract_committee_id','Employee', track_visibility='always',required=True,
                                    states={'draft': [('readonly', False)]})
    point_ids = fields.One2many(comodel_name='l10n_cu_contract.meeting_point',inverse_name='contract_committee_id',string='Puntos')
    description = fields.Text(string='Desarrollo')
    local_id = fields.Many2one('l10n_cu_locals.local', string="Local")
    start_time = fields.Float('Hora de inicio', default='08.00', required=True)
    stop_time = fields.Float('Hora de fin', default='09.00', required=True)
    hour_start_char = fields.Char('Hora inicial',compute='_compute_float_time_inicial',store=True)
    hour_end_char = fields.Char('Tiempo final',compute='_compute_float_time_final',store=True)
    month_name = fields.Char('Nombre del mes',compute='_get_month_name',store=True)
    city_name = fields.Char('Nombre de la Ciudad',related='company_id.city')

    @api.one
    @api.depends('date_committee')
    def _get_month_name(self):
        month = self.date_committee.split('-')
        month = month[1]
        if month == '01':
            self.month_name = 'Enero'
        elif month == '02':
            self.month_name = 'Febrero'
        elif month == '03':
            self.month_name ='Marzo'
        elif month == '04':
            self.month_name = 'Abril'
        elif month == '05':
            self.month_name = 'Mayo'
        elif month == '06':
            self.month_name = 'Junio'
        elif month == '07':
            self.month_name = 'Julio'
        elif month == '08':
            self.month_name = 'Agosto'
        elif month == '09':
            self.month_name = 'Septiembre'
        elif month == '10':
            self.month_name = 'Octubre'
        elif month == '11':
            self.month_name = 'Noviembre'
        elif month == '12':
            self.month_name = 'Diciembre'

    date_year = fields.Char('Año',compute='_get_year',store=True)

    @api.one
    @api.depends('date_committee')
    def _get_year(self):
        year = self.date_committee.split('-')
        year = year[0]
        self.date_year = year

    date_day = fields.Char('Día',compute='_get_day',store=True)

    @api.one
    @api.depends('date_committee')
    def _get_day(self):
        day = self.date_committee.split('-')
        day = day[2]
        self.date_day = day

    @api.one
    @api.depends('start_time')
    def _compute_float_time_inicial(self):

        if self.start_time:
            num = self.start_time
            hour = float(str(num).split('.')[0])
            float_min = (num - hour) * 100
            minut = '%(number)02d' % {"number": int((float_min * 60) / 100)}
            hour = '%(number)02d' % {"number": int(str(num).split('.')[0])}
            print hour + ':' + minut

            self.hour_start_char = hour + ':' + minut
        else:
            self.hour_start_char = ''

    @api.one
    @api.depends('stop_time')
    def _compute_float_time_final(self):

        if self.stop_time:
            num = self.stop_time
            hour = float(str(num).split('.')[0])
            float_min = (num - hour) * 100
            minut = '%(number)02d' % {"number": int((float_min * 60) / 100)}
            hour = '%(number)02d' % {"number": int(str(num).split('.')[0])}
            print hour + ':' + minut

            self.hour_end_char = hour + ':' + minut
        else:
            self.hour_end_char = ''




    @api.one
    @api.constrains('start_time', 'stop_time')
    def _check_start_stop_time(self):
        if self.start_time >= self.stop_time:
            raise ValidationError(_('Incompatible times: The stop time must be bigger than the start time of the meeting!'))

    @api.one
    def set_open(self):
        self.state = 'open'

    @api.multi
    def unlink(self):
        for obj in self:
            if obj.state != 'draft':
                raise UserError(_("Unlink in state draft."))
        return super(ContractCommittee, self).unlink()

    @api.one
    @api.constrains('nro_committee')
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

    _sql_constraints = [
        ('nro_committee_uniq', 'unique(nro_committee)', _("The number must be unique!")),
    ]
