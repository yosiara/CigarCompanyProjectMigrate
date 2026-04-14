# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Municipality(models.Model):
    _name = 'l10n_cu_base.municipality'
    _order = 'code'

    state_id = fields.Many2one('res.country.state', 'State', required=True)
    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('Code', size=3, help='The municipality code in three chars', required=True)





class District(models.Model):
    _name = 'l10n_cu_base.district'
    _order = 'code'

    municipality_id = fields.Many2one('l10n_cu_base.municipality', 'Municipality', required=True)
    name = fields.Char('District name', size=64)
    code = fields.Char('Code', size=3, help='The District code in three chars', required=True)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            code = record.code
            if record.name:
                code = "%s / %s" % (code, record.name)
            result.append((record.id, code))
        return result