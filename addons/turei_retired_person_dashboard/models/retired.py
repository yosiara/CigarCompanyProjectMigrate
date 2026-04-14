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


class RetiredDashboard(models.Model):
    _name = 'turei_retired_person_dashboard.dashboard'
    _description = 'Retired Person Dashboard'

    name = fields.Char("Name")

    @api.model
    def get_data_info(self):
        uid = request.session.uid
        cr = self.env.cr
        year = str(date.today())[0:4]
        data_info = []

        ist_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code','=','IST')])
        pc_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'PC')])
        spi_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'SPI')])
        ca_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'CA')])
        sg_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'SG')])
        dcf_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'DCF')])
        dch_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'DCH')])
        dtd_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'DTD')])
        pad_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'PAD')])
        de_retired_count = self.env['turei_retired_person.retired_person'].search_count([('ueb_id.code', '=', 'DE')])
        founder_retired_count = self.env['turei_retired_person.retired_person'].search_count([('founder', '=', True)])


        dead_retired_count = self.env['turei_retired_person.retired_person'].search_count([('dead_person', '=', True)])
        founder_retired_count_male = self.env['turei_retired_person.retired_person'].search_count([('founder', '=', True),('gender', '=', 'Male')])


        dead_retired_count_male = self.env['turei_retired_person.retired_person'].search_count([('dead_person', '=', True),('gender', '=', 'Male')])
        founder_retired_count_female = self.env['turei_retired_person.retired_person'].search_count(
            [('founder', '=', True), ('gender', '=', 'Female')])

        dead_retired_count_female = self.env['turei_retired_person.retired_person'].search_count(
            [('dead_person', '=', True), ('gender', '=', 'Female')])

        view_retired_id = self.env.ref('turei_retired_person_dashboard.retired_tree_dashboard').id

        data = {
            'view_retired_id': view_retired_id,
            'ist_retired_count': ist_retired_count,
            'pc_retired_count': pc_retired_count,
            'spi_retired_count': spi_retired_count,
            'ca_retired_count': ca_retired_count,
            'sg_retired_count': sg_retired_count,
            'dcf_retired_count': dcf_retired_count,
            'dch_retired_count': dch_retired_count,
            'dtd_retired_count': dtd_retired_count,
            'pad_retired_count': pad_retired_count,
            'de_retired_count': de_retired_count,
            'founder_retired_count': founder_retired_count,
            'dead_retired_count': dead_retired_count,
            'founder_retired_count_male': founder_retired_count_male,
            'dead_retired_count_male': dead_retired_count_male,
            'founder_retired_count_female': founder_retired_count_female,
            'dead_retired_count_female': dead_retired_count_female,

        }
        data_info.append(data)
        return data_info