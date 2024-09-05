# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Inspection(models.Model):
    _name = 'computers_inventory.inspection'
    _description = 'inspection'

    name = fields.Char(string='Inspection', default='Inspection')
    equipment_id = fields.Many2one('maintenance.equipment', string='Job Position', required=True)
    date = fields.Date (string='Date', required=True)
    department_id = fields.Many2one('hr.department', string='Area', required=True)
    observations = fields.Text(string='Observations', required=True)
    participants_ids = fields.Many2many('hr.employee', string="Participants", required=True)
    security_incident_ids = fields.Many2many('computers_inventory.security_incident', relation='computers_inventory_insp_sec_incident_rel', string='Security incidents', required=True)
    conclusions = fields.Text(string='Conclusions', required=True)

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id.department_id != "":
            self.department_id = self.equipment_id.department_id


