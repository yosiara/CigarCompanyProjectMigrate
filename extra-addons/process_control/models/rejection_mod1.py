# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class RejectionMod1(models.Model):
    _name = 'process_control.rejection_mod1'
    _inherits = {'process_control.rejection': 'rejection_id'}
    _description = 'Rejection Module 1'

    rejection_id = fields.Many2one(comodel_name='process_control.rejection', string='Rejection')
    production_cigarette = fields.Integer('Cigarette Production *', required=True)
    rejection_cigarette = fields.Integer('Cigarette Rejection *', required=True)

    @api.onchange('productive_line_id')
    def _onchange_productive_line_id(self):
        if self.productive_line_id.id is not self.machine_id.productive_line_id.id:
            rejection_mod1_recs = self.tecnolog_control_id.rejection_mod1_ids
            machine_recs = self.machine_id.search([('productive_line_id', '=', self.productive_line_id.id)])
            i = 0
            if len(rejection_mod1_recs) > 1:
                for m in range(len(machine_recs)-1):
                    if machine_recs[m].id == rejection_mod1_recs[-2].machine_id.id:
                        i = m + 1
                        break
            self.machine_id = machine_recs[i].id

    @api.onchange('tecnolog_control_id')
    def _onchange_tecnolog_control_id(self):
        self.productive_line_id = self.productive_line_id.search([('productive_section_id', '=', self.tecnolog_control_id.productive_section_id.id)], limit=1).id

    # @api.onchange('rejection_id')
    # def _get_default_turn_attendance(self):
    #     if self.tecnolog_control_id.turn_id and self.tecnolog_control_id.session:
    #         domain = [('session', '=', self.tecnolog_control_id.session), ('turn_id', '=', self.tecnolog_control_id.turn_id.id)]
    #         rejection_recs = self.tecnolog_control_id.rejection_mod1_ids.sorted(key=lambda r: r.turn_attendance_id.hour_from, reverse=True)
    #         next_turn_attendance = self.turn_attendance_id.search(domain + [('hour_from', '>', rejection_recs[0].turn_attendance_id.hour_from)], order='hour_from asc', limit=1)
    #         if next_turn_attendance: # Next Hour
    #             self.turn_attendance_id = next_turn_attendance.id
    #         else: # Overtime
    #             overtime = self.turn_attendance_id.search(domain + [('hour_from', '=', 0), ('hour_to', '=', 0)], order='hour_from asc', limit=1)
    #             if overtime:
    #                 self.turn_attendance_id = overtime.id