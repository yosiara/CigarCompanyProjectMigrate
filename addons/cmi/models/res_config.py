# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CmiConfiguration(models.TransientModel):
    _name = 'cmi.config.settings'
    _inherit = 'res.config.settings'

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env.user.company_id)
    dw_conn_id = fields.Many2one(related='company_id.dw_conn_id', string='Connexion Data Warehouse')
    job_dir = fields.Char(related='company_id.job_dir', string='Transformations file')
    pdi_dir = fields.Char(related='company_id.pdi_dir', string='Pentaho Data Integration Dir')
    email_list = fields.Char(string='Email List', related='company_id.email_list')