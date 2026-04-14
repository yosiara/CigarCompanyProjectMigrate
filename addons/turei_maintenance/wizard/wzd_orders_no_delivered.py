# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class WzdOrdersNoDelivered(models.TransientModel):
    _name = 'wzd.orders.no.delivered'

    date_start = fields.Date('Desde', required=True)
    date_end = fields.Date('Hasta', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'turei_maintenance.orders_no_delivered_report', data={
            'date_start': self.date_start,
            'date_end': self.date_end,
        })

