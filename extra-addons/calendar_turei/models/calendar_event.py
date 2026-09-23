# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    group_task = fields.Boolean(string='Group Task', default=False)
    organizational_groups_ids = fields.Many2many('calendar_turei.organizational_groups')
    short_name = fields.Char(string='Short Name *', size=30, required=True, default='')
    task_type = fields.Selection(
        selection=[
            ('plan', 'Plan'),
            ('extra_plan', 'Extra Plan'),
        ],
        string='Task Type *',
        default='plan',
        required=True,
    )
    priority = fields.Selection(
        selection=[
            ('1', 'Normal'),
            ('2', 'High'),
        ],
        string='Priority *',
        default='1',
        required=True,
    )

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange('group_task', 'organizational_groups_ids')
    def _onchange_organizational_groups_ids(self):
        """ Autocompletar asistentes desde los grupos organizativos """
        if not self.group_task:
            self.partner_ids = self.env.user.partner_id
            return
        partners = self.env.company.partner_id
        if self.organizational_groups_ids:
            partners |= self.organizational_groups_ids.members_groups_ids.employee_id.work_contact_id
        self.partner_ids = partners

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