# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools

class TecnologControl(models.Model):
    _name = 'process_control.tecnolog_control'
    _inherit = ["mail.activity.mixin", "mail.thread"]
    _description = "Modelo de Control Tecnológico"

    date = fields.Date(string="Fecha *", required=True, copy=True, default=fields.Date.today)
    turn_id = fields.Many2one(comodel_name="process_control.turn", string="Turno *", required=True)

    session = fields.Selection([
        ('morning', 'Mañana'),
        ('afternoon', 'Tarde'),
    ], string="Sesión *", required=True, default='morning')

    productive_section_id = fields.Many2one(comodel_name="process_control.productive_section", string="Módulo *", required=True)
    productive_capacity = fields.Integer('Capacidad Prod. *', required=False)
    plan_time = fields.Integer('Tmpo. Plan(Horas) *', required=False)

    interruption_ids = fields.One2many(comodel_name="process_control.interruption", inverse_name="tecnolog_control_id", string="Interrupciones")  
    rechazo_amf_ids = fields.One2many(comodel_name="process_control.rechazo_amf", inverse_name="tecnolog_control_id", string="Rechazo de las AMF")
    rechazo_mod1_ids = fields.One2many(comodel_name="process_control.rechazo_mod1", inverse_name="tecnolog_control_id", string="Rechazo 'NANO', 'SBO', 'SRC'")
    production_by_hours_ids = fields.One2many(comodel_name="process_control.production_by_hours", inverse_name="tecnolog_control_id", string="Producción Horaria")
    

    # Clear notebook data
    @api.onchange("productive_section_id", "turn_id", "session")
    def _onchange_productive_section_id(self):
        if self.productive_section_id:
            self.interruption_ids.unlink()
            self.rechazo_amf_ids.unlink()
            self.rechazo_mod1_ids.unlink()
            self.production_by_hours_ids.unlink()

    @api.model
    def default_get(self, fields):
        res = super(TecnologControl, self).default_get(fields)
        rec_last = self.search([], order='id desc', limit=1)
        if rec_last:
            res["date"] = rec_last.date
            res["turn_id"] = rec_last.turn_id.id
            res["session"] = rec_last.session
        return res

    # @api.onchange("turn_id")
    # def _get_default_hour(self):
    #     turn_attendance_obj = self.env["process_control.turn_attendance"]
    #     rec_last = turn_attendance_obj.search([], order='id desc', limit=1)
    #     next_hour_from = turn_attendance_obj.search([('hour_from', '>', rec_last.hour_from)], order='hour_from asc', limit=1) if rec_last else False
    #     self.turn_attendance_id = next_hour_from.id if next_hour_from else turn_attendance_obj.search([], order='hour_from asc', limit=1).id

    # def create_rechazo(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.action.act_window',
    #         'res_model': 'process_control.rechazo',
    #         'view_mode': 'form',
    #         'context': {
    #             'default_turn_id': self.turn_id,
    #             'default_session': self.session,
    #         }
    #     }