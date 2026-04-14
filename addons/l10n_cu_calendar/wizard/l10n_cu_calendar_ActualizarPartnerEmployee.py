# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging

_logger = logging.getLogger(__name__)
from odoo import models, api


class ActualizarPartnerEmployee(models.TransientModel):
    _name = "l10n_cu_calendar.actualizar_partner_employee"

    # COLUMNS
    # date_start = fields.Date(related='period_id.date_start', store=True, readonly=True)
    # date_end = fields.Date(related='period_id.date_stop', store=True, readonly=True)
    # period_id = fields.Many2one('l10n_cu_period.period', string='Period',required=True)
    # -------

    # Actualizar si el partner es un employee
    @api.multi
    def actualizar_partner_employee(self):
        # Overwrite translation
        translate = self.env['ir.translation'].search([('src', '=', 'Meetings')])
        for t in translate:
            t.write({'value': 'Tareas'})

        # TODO:CHECK VARIUS EMPLOYEES WITH THE SAME USER
        # Se Cambio para el modelo hr.employee para realizar esta tarea cuando se modifica un empleado
        # for emp in self.env['hr.employee'].search([]):
        #     job = 'no defindo'
        #     boss_id = False
        #     department_id = False
        #     if emp.user_id:
        #         partner_id = emp.user_id.partner_id.id
        #         if emp.job_id:
        #             job = emp.job_id.name
        #         if emp.parent_id and emp.parent_id.user_id:
        #             boss_id = emp.parent_id.user_id.partner_id.id
        #         if emp.department_id:
        #             department_id = emp.department_id.id
        #         partner = self.env['res.partner'].browse(partner_id)
        #         partner.write({'employee': True,
        #                        'customer': False,
        #                        'function': job,
        #                        'boss_id': boss_id,
        #                        'department_id': department_id,
        #                        'email': emp.work_email,
        #                        'notify_email': 'always',
        #                        'user_id': emp.user_id.id
        #                        })

        # Delete from de group the inactive employees
        # Se Desactiva esto por el momento ya que si hay empleados inactivos con el mismo usuario
        # que un empleado activo elimina tambien el empleado activo de los grupos
        # for g in self.env['l10n_cu_calendar.org_group'].search([]):
        #     partners = g.partner_group_ids.ids
        #     old_size = len(partners)
        #     for inact_emp in self.env['hr.employee'].search([('active', '=', False)]):
        #         if inact_emp.user_id.partner_id.employee:
        #             inact_emp.user_id.partner_id.write({'employee': False})
        #         if inact_emp.user_id.partner_id.id in partners:
        #             partners.remove(inact_emp.user_id.partner_id.id)
        #     if len(partners) < old_size:
        #         g.write({'partner_group_ids': [(6, 0, partners)]})

        return True
