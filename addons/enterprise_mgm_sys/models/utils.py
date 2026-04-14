# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class WorkArea(models.Model):
    _name = 'enterprise_mgm_sys.work_area'

    name = fields.Char(string='Name', required=True)


class Month(models.Model):
    _name = 'enterprise_mgm_sys.month'

    name = fields.Char('Name', required=True)
    number = fields.Selection(string="Number", selection=[('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'),
                                        ('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'),
                                        ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12')], required=True)



    

