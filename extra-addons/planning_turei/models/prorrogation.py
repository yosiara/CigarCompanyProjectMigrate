from odoo import models, fields, api, _

class Prorrogation(models.Model):
    _name = 'planning_turei.prorrogation'
    _description = 'Planning Turei Prorrogation'

    name = fields.Text(string='Causa')
    request_date = fields.Date(string='Fecha Solicitud')
    prorogue_proposed_date = fields.Date(string='Fecha Aprobada')
    planning_slot_id = fields.Many2one('planning.slot')