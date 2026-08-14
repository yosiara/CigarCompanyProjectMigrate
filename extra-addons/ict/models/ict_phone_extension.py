# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ICTPhoneExtension(models.Model):
    _name = 'ict.phone.extension'
    _description = 'ICT Phone Extension'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'number'

    display_name = fields.Char(string='Display Name', compute='_compute_display_name')
    number = fields.Char(string='Extension Number', required=True, index=True)
    assign_date = fields.Date(string='Assignment Date', compute='_compute_assign_date')
    notes = fields.Html(string='Notes')
    extension_type = fields.Selection([
        ('fixed', 'Fixed Line'),
        ('voip', 'VoIP'),
        ('virtual', 'Virtual'),
    ], string='Extension Type', default='fixed', required=True)
    employee_id = fields.Many2one(
        comodel_name='ict.employee',
        string='Assigned Employee',
        tracking=True,
        ondelete='restrict',
        help='Employee assigned to this extension',
    )
    department_id = fields.Many2one(comodel_name='hr.department', string='Department', tracking=True)
    assign_to = fields.Selection(
        [('department', 'Department'), ('employee', 'Employee')],
        string='Used By',
        required=True,
        default='employee',
    )

    # ============================================================
    # CONSTRAINS
    # ============================================================
    _sql_constraints = [
        ('unique_number', 'unique(number)', 'Extension number must be unique.'),
    ]

    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    @api.depends('number', 'employee_id', 'department_id')
    def _compute_display_name(self):
        for ext in self:
            if ext.employee_id:
                ext.display_name = f"{ext.number} - {ext.employee_id.name.split()[0]}"
            elif ext.department_id:
                ext.display_name = f"{ext.number} - {ext.department_id.name}"
            else:
                ext.display_name = ext.display_name

    @api.depends("employee_id", "department_id")
    def _compute_assign_date(self):
        for ext in self:
            ext.assign_date = fields.Date.context_today(self) if ext.employee_id or ext.department_id else False

    # ============================================================
    # ONCHANGE METHODS
    # ============================================================
    @api.onchange("assign_to")
    def _onchange_productive_line_id(self):
        if self.assign_to == 'employee' and self.department_id:
            self.department_id = False
        elif self.assign_to == 'department' and self.employee_id:
            self.employee_id = False

    # @api.model_create_multi
    # def create(self, vals_list):
    #     extensions = super().create(vals_list)
    #     for ext in extensions:
    #         ext._sync_employee_work_phone()
    #         # Si es asignada a un empleado, marcar como principal si no hay otra
    #         if ext.employee_id and not ext.is_primary:
    #             ext._ensure_primary_extension()
    #     return extensions

    # def write(self, vals):
    #     # Guardar cambios de employee_id o number para sincronizar después
    #     old_employees = {ext.id: ext.employee_id for ext in self}
    #     res = super().write(vals)
        
    #     # Sincronizar el teléfono de trabajo del empleado
    #     if 'employee_id' in vals or 'number' in vals or 'is_primary' in vals:
    #         for ext in self:
    #             ext._sync_employee_work_phone()
        
    #     # Si se desasignó de un empleado, recalcular su work_phone desde otras extensiones
    #     if 'employee_id' in vals and not vals.get('employee_id'):
    #         for ext in self:
    #             old_emp = old_employees.get(ext.id)
    #             if old_emp:
    #                 old_emp._update_work_phone_from_extensions()
        
    #     # Si se asignó a un empleado y no es principal, asegurar una principal
    #     if 'employee_id' in vals and vals.get('employee_id'):
    #         for ext in self:
    #             if not ext.is_primary:
    #                 ext._ensure_primary_extension()
        
    #     return res

    # def _sync_employee_work_phone(self):
    #     """Sincroniza el work_phone del empleado con esta extensión si es la principal."""
    #     if self.employee_id and self.is_primary and self.number:
    #         hr_emp = self.employee_id.employee_id
    #         if hr_emp and hr_emp.work_phone != self.number:
    #             hr_emp.work_phone = self.number

    # def _ensure_primary_extension(self):
    #     """Asegura que haya una extensión principal para el empleado."""
    #     if not self.employee_id:
    #         return
        
    #     # Buscar si ya hay una principal
    #     primary = self.search([
    #         ('employee_id', '=', self.employee_id.id),
    #         ('is_primary', '=', True),
    #     ], limit=1)
        
    #     if not primary:
    #         # No hay principal, marcar esta como principal
    #         self.is_primary = True
    #         # Sincronizar work_phone
    #         self._sync_employee_work_phone()
    #     elif primary != self and self.is_primary:
    #         # Si esta es principal pero ya hay otra, desmarcar esta
    #         self.is_primary = False
    #         # Asegurar que la otra sigue siendo principal (ya lo es)

    # def action_set_primary(self):
    #     """Acción para marcar esta extensión como principal desde el formulario."""
    #     self.ensure_one()
    #     if self.employee_id:
    #         # Desmarcar otras principales del mismo empleado
    #         self.search([
    #             ('employee_id', '=', self.employee_id.id),
    #             ('is_primary', '=', True),
    #         ]).write({'is_primary': False})
    #         self.is_primary = True
    #         self._sync_employee_work_phone()
    #     else:
    #         raise UserError(_("Cannot set as primary: no employee assigned."))