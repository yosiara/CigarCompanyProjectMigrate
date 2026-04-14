# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class ProductionByHours(models.Model):
    _name = 'process_control.production_by_hours'
    _description = "Production By Hours"

    turn_att_id = fields.Many2one('process_control.turn_attendance', string='Hora *', required=True)
    production_count = fields.Float(string='Producción (Cajones) *', required=True)

    tecnolog_control_id = fields.Many2one(comodel_name="process_control.tecnolog_control", string="Modelo Control", ondelete='cascade', required=True)

    @api.onchange("tecnolog_control_id")
    def _onchange_tecnolog_control_id(self):
        domain = [('turn_id', '=', self.tecnolog_control_id.turn_id.id), ('session', '=', self.tecnolog_control_id.session)]
        production_by_hours_recs = self.tecnolog_control_id.production_by_hours_ids.sorted(lambda r: r.turn_att_id.hour_from, reverse=True)
        att_next_rec = self.turn_att_id.search(domain + [('hour_from', '>', production_by_hours_recs[0].turn_att_id.hour_from)], order="hour_from asc", limit=1)
        self.turn_att_id = att_next_rec.id if att_next_rec else self.turn_att_id.search(domain + [('hour_from', '=', 0), ('hour_to', '=', 0)], limit=1).id