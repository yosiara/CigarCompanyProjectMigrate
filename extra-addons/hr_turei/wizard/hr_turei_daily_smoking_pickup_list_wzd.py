# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiDailySmokinPickUpgWzd(models.TransientModel):
    _name = 'hr_turei.daily_smoking_pickup_wzd'

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    elaborated_by = fields.Many2one('hr.employee', 'Elaborated By', required=True)
    approved_by = fields.Many2one('hr.employee', 'Approved By', required=True)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'hr_turei.daily_smoking_pickup_list', data={
            'company_id': self.company_id.id,
            'elaborated_by': self.elaborated_by.id,
            'approved_by': self.approved_by.id
        })

