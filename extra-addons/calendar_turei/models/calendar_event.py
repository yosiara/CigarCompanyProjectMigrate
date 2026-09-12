# -*- coding: utf-8 -*-
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

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('organizational_groups_ids')
    def _onchange_organizational_groups_ids(self):
        """Autocompletar partners/asistentes según grupos organizativos seleccionados"""
        partner_ids = self.env['res.partner']
        for group in self.organizational_groups_ids:
            for member in group.members_groups_ids:
                if member.employee_id.work_contact_id:
                    partner_ids |= member.employee_id.work_contact_id
        self.partner_ids = partner_ids

    # ============================================================
    # OVERRIDE METHODS
    # ============================================================
    @api.depends('partner_ids')
    @api.depends_context('uid')
    def _compute_user_can_edit(self):
        super()._compute_user_can_edit()

        # Añadimos nuestros editores extra
        is_calendar_manager = self.env.user.has_group(
            'calendar_turei.group_calendar_turei_manager'
        )
        if not is_calendar_manager:
            return

        for event in self:
            if not event.user_can_edit and event.privacy != 'private':
                event.user_can_edit = True