# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    code = fields.Char('Company code')
    job_dir = fields.Char('Transformations file')
    pdi_dir = fields.Char('Pentaho Data Integration Dir')
    dw_conn_id = fields.Many2one('db_external_connector.template', 'Connexion Data Warehouse')
    email_list = fields.Char('Email List', help="Email address to send information about indicators' state.")