# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class TecnologControl(models.Model):
    _name = 'process_control.tecnolog_control'
    _inherit = ['mail.activity.mixin', 'mail.thread']
    _description = 'Tecnolog Control'

    date = fields.Date(string='Date *', required=True, copy=True, default=fields.Date.today)
    turn_id = fields.Many2one(comodel_name='process_control.turn', string='Turn *', required=True)

    session = fields.Selection([
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
    ], string='Session *', required=True, default='morning')

    productive_section_id = fields.Many2one(comodel_name='process_control.productive_section', string='Productive Section *', required=True)
    productive_capacity = fields.Integer('Productive Capacity *')
    plan_time = fields.Integer('Plan Time (Hour) *')

    interruption_ids = fields.One2many(comodel_name='process_control.interruption', inverse_name='tecnolog_control_id', string='Interruptions')  
    rejection_amf_ids = fields.One2many(comodel_name='process_control.rejection_amf', inverse_name='tecnolog_control_id', string='Rejection AMF')
    rejection_mod1_ids = fields.One2many(comodel_name='process_control.rejection_mod1', inverse_name='tecnolog_control_id', string='Rejection (NANO, SBO, SRC)')
    production_by_hours_ids = fields.One2many(comodel_name='process_control.production_by_hours', inverse_name='tecnolog_control_id', string='Hourly Production')
    
    # Clear notebook data
    @api.onchange('productive_section_id', 'turn_id', 'session')
    def _onchange_productive_section_id(self):
        if self.productive_section_id:
            self.interruption_ids.unlink()
            self.rejection_amf_ids.unlink()
            self.rejection_mod1_ids.unlink()
            self.production_by_hours_ids.unlink()

    @api.model
    def default_get(self, fields):
        res = super(TecnologControl, self).default_get(fields)
        rec_last = self.search([], order='id desc', limit=1)
        if rec_last:
            res['date'] = rec_last.date
            res['turn_id'] = rec_last.turn_id.id
            res['session'] = rec_last.session
        return res

    # @api.onchange('turn_id')
    # def _get_default_hour(self):
    #     turn_attendance_obj = self.env['process_control.turn_attendance']
    #     rec_last = turn_attendance_obj.search([], order='id desc', limit=1)
    #     next_hour_from = turn_attendance_obj.search([('hour_from', '>', rec_last.hour_from)], order='hour_from asc', limit=1) if rec_last else False
    #     self.turn_attendance_id = next_hour_from.id if next_hour_from else turn_attendance_obj.search([], order='hour_from asc', limit=1).id

    # def create_rejection(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.action.act_window',
    #         'res_model': 'process_control.rejection',
    #         'view_mode': 'form',
    #         'context': {
    #             'default_turn_id': self.turn_id,
    #             'default_session': self.session,
    #         }
    #     }