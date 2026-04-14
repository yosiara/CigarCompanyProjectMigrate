# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class IncidentPlan(models.Model):
    _name = 'turei_maintenance.incident_plan'
    _rec_name = 'description'

    date_start = fields.Date('Fecha Inicio', required=True)
    date_end = fields.Date('Fecha Fin', required=True)
    description = fields.Text(string="Descripción")
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)

    @api.multi
    @api.depends('date_start')
    def _compute_year_char(self):
        for c_model in self:
            date_start = fields.datetime.strptime(c_model.date_start, DEFAULT_SERVER_DATE_FORMAT)
            c_model.year_char = str(date_start.year)

    @api.model
    def create(self, vals):
        res = super(IncidentPlan, self).create(vals)

        return res


