# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import api, fields, models, Command
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)


class Event(models.Model):
    _inherit = 'calendar.event'
    _order = 'start ASC'

    group_task = fields.Boolean('Tarea de Grupo', default=False)
    organizational_groups_ids = fields.Many2many('calendar_turei.organizational_groups')
    short_name = fields.Char(string='Nombre corto', size=30, required=True)
    task_type = fields.Selection([('Plan', 'Plan'), ('Extra Plan', 'Extra Plan')], string='Tipo', default='Plan', required=True)
    priority = fields.Selection([('1', 'Normal'), ('2', 'Alta')], string='Prioridad', default='1', required=True)
    user_id = fields.Many2one('res.users', 'Organizer', default=False, required=True)

    @api.onchange('organizational_groups_ids')
    def _onchange_organizational_groups_ids(self):
        partner_ids = []
        if self.organizational_groups_ids:
            for grupo in self.organizational_groups_ids:
                for integrante in grupo.members_groups_ids:
                    if integrante.employee_id.user_id:
                        partner_ids.append(integrante.employee_id.user_id.partner_id.id)
        self.partner_ids = self.env['res.partner'].browse(partner_ids)

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.partner_ids += self.user_id.partner_id

