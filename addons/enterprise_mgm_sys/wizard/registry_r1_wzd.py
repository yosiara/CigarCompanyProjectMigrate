# -*- coding: utf-8 -*-


from odoo import models, fields, tools
from datetime import datetime, date


class RegistryR1Wzd(models.TransientModel):
    _name = 'enterprise_mgm_sys.registry_r1_wzd'

    def _default_start(self):
        return date(datetime.today().year, 1, 1)

    def _default_end(self):
        return date(datetime.today().year, 12, 31)

    all_company = fields.Boolean(string='All Company', required=True)
    area_id = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Segment or Unit')
    start = fields.Date(string='Start', required=True, default=_default_start)
    end = fields.Date(string='End', required=True, default=_default_end)
    realization_date = fields.Date(string='Realization Date', required=True, default=lambda today: datetime.today())

    def export_to_xls(self):
        action = self.env['report'].get_action(self, 'enterprise_mgm_sys.registry_r1_resume_report')
        action['datas'] = {
                'all_company': self.all_company,
                'area_id': self.area_id.id,
                'start': self.start,
                'end': self.end,
                'realization_date': self.realization_date
            }
        return action
