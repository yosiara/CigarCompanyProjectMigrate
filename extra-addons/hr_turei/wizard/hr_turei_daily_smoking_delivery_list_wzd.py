# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiDailySmokingDeliveryWzd(models.TransientModel):
    _name = 'hr_turei.daily_smoking_delivery_wzd'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    date = fields.Date('Date', default=lambda self: fields.Date.today(), required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'hr_turei.daily_smoking_delivery_list', data={
            'date': self.date
        })

