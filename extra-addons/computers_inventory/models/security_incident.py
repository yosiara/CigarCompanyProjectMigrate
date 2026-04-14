# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools
import datetime


class SecurityIncident(models.Model):
    _name = 'computers_inventory.security_incident'
    _description = 'Security Incident'
    _inherit = 'computers_inventory.send_mail_mixin'

    name = fields.Char(string='Security Incident', default='Security Incident')
    id_code = fields.Char(string='Identification code', help="The incidents detected in one year are listed in ascending order starting from 1 acording to the registration date. The security incidents have a unique identifier composed of: [characters \"IS#\"]+[\"number of order of the incident in the year that was detected\"]+[character \"/\"]+[\"year of detection\"], so IS#1/2019 would be the correct identifier for the first insident detected on the year 2019.")
    equipment_id = fields.Many2one('maintenance.equipment', string='Computer', required=True)
    employee_id = fields.Many2one('hr.employee', string='Responsable', required=True)
    department_id = fields.Many2one('hr.department', string='Area', required=True)
    datetime_start = fields.Datetime(string='Datetime start')
    datetime_end = fields.Datetime(string='Datetime end')
    incident = fields.Text(string='Incident', required=True)
    detection_date = fields.Date(string='Detection date', required=True)
    detector = fields.Many2one('hr.employee', string='Detector', required=True)
    observations = fields.Text(string='Observations')
    provisions_applied = fields.Text(string='Provisions applied', required=True)

    @api.onchange('equipment_id')
    def _onchange_equipment_id(self):
        if self.equipment_id.employee_id != "":
            self.employee_id = self.equipment_id.employee_id
        if self.equipment_id.department_id != "":
            self.department_id = self.equipment_id.department_id

    @api.onchange('detection_date')
    def _onchange_detection_date(self):
        id_code = ''
        actual_date = str(datetime.datetime.now())
        there_year_security_insidents_list = self.env['computers_inventory.security_incident'].search(
            [('detection_date', 'like', str(self.detection_date)[0:4])])
        if len(there_year_security_insidents_list) == 0:
            id_code = 'IS#1/' + str(self.detection_date)[0:4]
        else:
            id_code = "IS#" + str(len(there_year_security_insidents_list) + 1) + '/' + str(self.detection_date)[0:4]

        self.id_code = id_code
        self.name = id_code

    @api.model
    def create(self, vals):
        res = super(SecurityIncident, self).create(vals)
        recipients = self.get_computer_inventory_responsible()
        recipients = list(set(recipients))
        res.send_mail('l10n_cu_hlg_computers_inventory.computer_inventory_template_security_incident', force_send=False, recipients=recipients)
        return res









