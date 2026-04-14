# -*- coding: utf-8 -*-
##############################################################################
from odoo.http import request
import datetime
from datetime import date
from odoo import api, fields, models, _
import json
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF


class EnterpriseMgmSysDashboard(models.Model):
    _name = 'enterprise_mgm_sys.dashboard'

    name = fields.Char("Name")
    process_map = fields.Binary(string="Process Map")

    @api.model
    def get_data_info(self):
        obj = self.env['enterprise_mgm_sys.dashboard'].search([], limit=1)
        processes = self.env['enterprise_mgm_sys.process'].search([])
        process_list = []
        for process in processes:
            item = {
                'id': process.id,
                'name': process.name,
                'href': False,
                'process_file_id': False,
            }
            if process.process_file and process.process_file.line_ids:
                process_file = process.process_file.line_ids[0]
                if process_file.link_type == 'file':
                    item['process_file_id'] = process_file.id
                else:
                    item['href'] = process_file.external_url

            process_list.append(item)

        if obj:
            data_info = {
                'process_map': obj.process_map,
                'name': obj.name,
                'processes': process_list,
                'docs': self.env['enterprise_mgm_sys.registry'].search_count([]),
                'agreements': self.env['enterprise_mgm_sys.internal_agreement'].search_count([]),
                'audits': self.env['enterprise_mgm_sys.audit'].search_count([]),
                'no_conformities': self.env['enterprise_mgm_sys.no_conformity'].search_count([]),
            }
            return data_info
        else:
            return {}