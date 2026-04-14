# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError


class Ministry(models.Model):
    _name = 'l10n_cu.ministry'
    name = fields.Char('Name', required=True)


class Branch(models.Model):
    _name = 'l10n_cu.branch'

    name = fields.Char('Name', required=True)


class PartnerLocation(models.Model):
    _name = 'l10n_cu_hlg.partner_location'

    name = fields.Char('Name', required=True)
    street = fields.Char('Street')
    partner_id = fields.Many2one('res.partner', 'Partner')
    fleet_route_id = fields.Many2one('fleet.route', string='Fleet route')


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_default_country(self):
        return 52

    ci = fields.Char('CI')
    reeup_code = fields.Char('REEUP Code')
    nit_code = fields.Char('NIT Code')
    # nae_code = fields.Char('NAE Code')
    usd_license_number = fields.Char('No. de Licencia de Operación en Divisa')
    date_license_number = fields.Date('Fecha de Licencia Operativa en Divisa')
    short_name = fields.Char('Short Name')
    municipality_id = fields.Many2one('l10n_cu_base.municipality', 'Municipality')
    ministry_id = fields.Many2one('l10n_cu.ministry', 'Ministry')
    branch_id = fields.Many2one('l10n_cu.branch', 'Branch')
    archive_nro = fields.Char('Archive Nro')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', default=_get_default_country)
    # Accreditation
    acc_res_no = fields.Char('Resolution Nro')
    acc_res_date = fields.Date('Resolution Date')
    acc_res_date_day = fields.Char('Resolution Day', compute='_get_resolution_day', store=True)
    mercantil_register = fields.Char('Registro Mercantil')
    code_swift = fields.Char('Código SWIFT')

    @api.depends('acc_res_date')
    @api.one
    def _get_resolution_day(self):
        if self.acc_res_date:
            date = self.acc_res_date
            date = date.split('-')
            self.acc_res_date_day = date[2]

    acc_res_date_month = fields.Char('Resolution Month', compute='_get_resolution_month', store=True)

    @api.depends('acc_res_date')
    @api.one
    def _get_resolution_month(self):
        if self.acc_res_date:
            date = self.acc_res_date
            date = date.split('-')
            self.acc_res_date_month = date[1]

    acc_res_date_year = fields.Char('Resolution Year', compute='_get_resolution_year', store=True)

    @api.depends('acc_res_date')
    @api.one
    def _get_resolution_year(self):
        if self.acc_res_date:
            date = self.acc_res_date
            date = date.split('-')
            self.acc_res_date_year = date[0]

    acc_res_emitted = fields.Char('Emitted by')

    acc_res_no_boss = fields.Char('Resolution Nro')
    acc_res_date_boss = fields.Date('Resolution Date')
    acc_res_emitted_boss = fields.Char('Emitted by')
    acc_res_position_boss = fields.Char('Position')
    acc_res_name_boss = fields.Char('Name')
    # Contract
    authorized = fields.Boolean("Authorized to firm contract")
    authorized_by = fields.Char("Authorized By")
    approve_charge = fields.Char("Approve Charge")
    approve_res_no = fields.Char("Resolution Nro")
    approve_res_date = fields.Date("Resolution Date")
    # Invoice
    authorized_invoice = fields.Boolean("Authorized to firm invoice")
    authorized_by_invoice = fields.Char("Authorized By")
    approve_charge_invoice = fields.Char("Approve Charge")
    approve_res_no_invoice = fields.Char("Resolution Nro")
    approve_res_date_invoice = fields.Date("Resolution Date")
    partner_location_ids = fields.One2many(
        'l10n_cu_hlg.partner_location', 'partner_id', 'Partner Location')
    # reconcile
    authorized_reconcile = fields.Boolean("Autorizado a firmar conciliaciones")
    # solicitar servicios
    authorized_apply = fields.Boolean("Autorizado a solicitar servicios")

    @api.onchange('municipality_id')
    def _onchange_municipality_id(self):
        if self.municipality_id:
            self.state_id = self.municipality_id.state_id.id

    @api.onchange('state_id')
    def _onchange_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('name', operator, name), ('reeup_code', operator, name),
                      ('short_name', operator, name)]
        pos = self.search(domain + args, limit=limit)
        return pos.name_get()

    @api.constrains('acc_res_date')
    def _check_date_acc(self):
        if self.acc_res_date:
            if datetime.strptime(self.acc_res_date, '%Y-%m-%d') > datetime.today():
                raise ValidationError(_('Error! Resolution date must be less than the current date.'))
