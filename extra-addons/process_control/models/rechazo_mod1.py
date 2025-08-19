# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class RechazoMod1(models.Model):
    _name = 'process_control.rechazo_mod1'
    _inherits = {"process_control.rechazo": "rechazo_id"}
    _description = "Rechazo Módulo 1"

    _sql_constraints = [
        ('rechazo_uniq', 'unique(rechazo_id)', 'Por cada registro en rechazo Módulo 1, un único registro de rechazo asociado en el padre.'),
    ]

    rechazo_id = fields.Many2one(comodel_name='process_control.rechazo', string='Rechazo')
    
    prod_en_cigarrillos = fields.Integer('Produción en cigarrillos *', required=True)
    rechazo_en_cigarrillos = fields.Integer('Rechazo en cigarrillos *', required=True)
    #prod_en_cajetillas = fields.Integer('Producción en cajetillas')

    @api.onchange("productive_line_id")
    def _onchange_productive_line_id(self):
        if self.productive_line_id.id is not self.machine_id.productive_line_id.id:
            rechazo_mod1_recs = self.tecnolog_control_id.rechazo_mod1_ids
            machine_recs = self.machine_id.search([('productive_line_id', '=', self.productive_line_id.id)])
            i = 0
            if len(rechazo_mod1_recs) > 1:
                for m in range(len(machine_recs)-1):
                    if machine_recs[m].id == rechazo_mod1_recs[-2].machine_id.id:
                        i = m + 1
                        break
            self.machine_id = machine_recs[i].id

    @api.onchange("tecnolog_control_id")
    def _onchange_tecnolog_control_id(self):
        self.productive_line_id = self.productive_line_id.search([('productive_section_id', '=', self.tecnolog_control_id.productive_section_id.id)], limit=1).id

    # @api.onchange("rechazo_id")
    # def _get_default_turn_attendance(self):
    #     if self.tecnolog_control_id.turn_id and self.tecnolog_control_id.session:
    #         domain = [('session', '=', self.tecnolog_control_id.session), ('turn_id', '=', self.tecnolog_control_id.turn_id.id)]
    #         rechazo_recs = self.tecnolog_control_id.rechazo_mod1_ids.sorted(key=lambda r: r.turn_attendance_id.hour_from, reverse=True)
    #         next_turn_attendance = self.turn_attendance_id.search(domain + [('hour_from', '>', rechazo_recs[0].turn_attendance_id.hour_from)], order='hour_from asc', limit=1)
    #         if next_turn_attendance: # Next Hour
    #             self.turn_attendance_id = next_turn_attendance.id
    #         else: # Overtime
    #             overtime = self.turn_attendance_id.search(domain + [('hour_from', '=', 0), ('hour_to', '=', 0)], order='hour_from asc', limit=1)
    #             if overtime:
    #                 self.turn_attendance_id = overtime.id