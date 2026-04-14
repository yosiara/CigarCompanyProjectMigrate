# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    organism_id = fields.Many2one('l10n_cu_hlg_uforce.organism', string='Organism')
    gforza_code = fields.Char(string='Entity Code')  # use in XML GFORZA
    is_gfroza_entity = fields.Boolean(string='Is a Entity', compute='_compute_is_gfroza_entity', store=True)

    @api.multi
    def _compute_is_gfroza_entity(self):
        companies = []
        for c in self.env['res.company'].search([]):
            if c.partner_id.id and c.partner_id.id not in companies:
                companies.append(c.partner_id.id)
        for res in self:
            res.is_gfroza_entity = (res.id in companies)


class Company(models.Model):
    _inherit = 'res.company'

    organism_id = fields.Many2one(related='partner_id.organism_id', string='Organism', store=True)
    ministry_id = fields.Many2one(related='partner_id.ministry_id', string='Ministry', store=True)
    gforza_code = fields.Char(related='partner_id.gforza_code', string='Entity Code', store=True)  # use in XML GFORZA


class Ministry(models.Model):
    _inherit = 'l10n_cu.ministry'

    code = fields.Char(string='Code')


class CountryState(models.Model):
    _inherit = 'res.country.state'

    external_id = fields.Integer(string='External ID')


class Municipality(models.Model):
    _inherit = 'l10n_cu_base.municipality'

    external_id = fields.Integer(string='External ID')
