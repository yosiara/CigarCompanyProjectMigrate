from odoo import models, fields, api, _

class Prorogation(models.Model):
    _name = 'planning_turei.prorogation'
    _description = 'Planning Turei Prorogation'
    
    request_date = fields.Date(string='Fecha Solicitada', default=fields.Date().today())
    cause = fields.Text(string='Causa')
    proposed_date = fields.Date(string='Fecha Propuesta')
    is_approved = fields.Boolean(string='Aprobar')
    planning_slot_id = fields.Many2one('planning.slot')

    # @api.onchange('prorogue_approve')
    # def _onchange_prorogue_approve(self):
    #     if self.prorogue_approve:
    #         self.write({
    #             'prorrogation_ids': [(0, 0, {
    #                 'name': self.prorogue_cause,
    #                 'request_date': self.request_date,
    #                 'prorogue_proposed_date': self.prorogue_proposed_date,
    #             })]
    #         })
    #         self.prorogue = False