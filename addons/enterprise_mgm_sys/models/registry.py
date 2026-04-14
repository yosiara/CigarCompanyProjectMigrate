# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import json


class RegistryLine(models.Model):
    _name = 'enterprise_mgm_sys.registry_line'

    _order = 'approved_date desc,id'

    registry_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.registry',
        string='Registry',
        required=True, ondelete='cascade')
    name = fields.Char(string='Name', related='registry_id.name')
    version = fields.Char(string='Version', required=False)
    agreement_number = fields.Char(string='Agreement Number', required=False)
    approved_date = fields.Date(string='Approved Date', required=False)
    resolution_number = fields.Char(string='Resolution number', required=False)
    description = fields.Text(string="Description", required=False)
    link_type = fields.Selection(string='Link type', selection=[('web', 'Web'), ('file', 'File'), ], required=False, default='web')
    external_url = fields.Char(string='External url', required=False)
    file = fields.Binary(string="File")


class Registry(models.Model):
    _name = 'enterprise_mgm_sys.registry'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    type = fields.Selection(
        string='Type',
        selection=[('process_file', 'Process File'), ('procedure', 'Procedure'), ('manual', 'Manual'),
                   ('work_instruction', 'Work Instruction'), ('work_document', 'Work Document')],
        required=True, )
    version = fields.Char(string='Version', required=False, compute='_compute_values', store=True)
    agreement_number = fields.Char(string='Agreement Number', required=False, compute='_compute_values', store=True)
    approved_date = fields.Date(string='Approved Date', required=False, compute='_compute_values', store=True)
    resolution_number = fields.Char(string='Resolution number', required=False, compute='_compute_values', store=True)
    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process', required=False)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.registry_line',
        inverse_name='registry_id',
        string='Changes',
        required=False)

    @api.depends('line_ids')
    def _compute_values(self):
        for record in self:
            if record.line_ids:
                record.version = record.line_ids[0].version
                record.agreement_number = record.line_ids[0].agreement_number
                record.approved_date = record.line_ids[0].approved_date
                record.resolution_number = record.line_ids[0].resolution_number

    def download_file(self):
        if self.line_ids:
            if self.line_ids[0].link_type == 'file':
                return {
                    'type': 'ir.actions.act_url',
                    'name': _("Download File"),
                    'target': 'new',
                    'url': '/web/content/enterprise_mgm_sys.registry_line/%s/file/%s' % (self.line_ids[0].id, self.name)
                }
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'name': _("Download File"),
                    'target': 'new',
                    'url': self.line_ids[0].external_url
                }
