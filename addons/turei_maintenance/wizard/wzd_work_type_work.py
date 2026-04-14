# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdWorkTypeWork(models.TransientModel):
    _name = 'wzd.work.type.work'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.work_type_work_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
        })

