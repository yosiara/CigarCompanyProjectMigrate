from odoo import models, fields, api, _
import logging
from datetime import timedelta
from odoo.tools import float_utils
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class PlanningSlot(models.Model):
    _inherit = 'planning.slot'

    # -------------------------------------------------------------------------
    # DEFAULT METHODS                                                         #
    # -------------------------------------------------------------------------
    def _default_next_task_seq(self):
        seq = self.env['ir.sequence'].search([('code', '=', 'planning.slot.task_seq')], limit=1)
        if not seq:
            return _("New")
        return seq.get_next_char(number_next=seq.number_next_actual)

    task_seq = fields.Char(string='N° Consecutivo', readonly=True, copy=False, index=True, default=_default_next_task_seq)
    subcommissions_id = fields.Many2one(comodel_name='planning_turei.subcommissions', string='Subcomisión', required=True, ondelete='cascade')
    subcommissions_domain = fields.Binary(compute="_get_subcommissions_domain", exportable=False)
    ejecutor_id = fields.Many2one('hr.employee', string='Ejecuta')
    child_ids = fields.One2many('hr.employee', 'planning_slot_id')

    # Conformity
    conformity = fields.Boolean(string='Conformidad')
    conformity_date = fields.Date(string='Fecha de Conformidad', default=fields.Date().today())
    show_conformity = fields.Boolean(string='Mostrar Conformidad', compute='_compute_controla_cumplimiento')
    agreement_number = fields.Char(string='Nro. Acuerdo')

    # Compliance fields
    control_compliance_id = fields.Many2one('hr.employee', string='Ctrl. Cumpl.')
    accomplished = fields.Boolean(string='Cumplido')
    compliance_info = fields.Text(string='Inf. Cumplimiento')
    compliance_date = fields.Date(string='Fecha Cumplimiento', default=fields.Date().today())
    compliance_date_real = fields.Date(string='Cumpl. Real', default=fields.Date().today())
    compliance_real_show = fields.Boolean(string='Mostrar Fecha Real')
    task_closure = fields.Selection([('Cumplido', 'Cumplido'), ('Incumplido', 'Incumplido'), ('Derogado', 'Derogado')], string='Cumplimiento')
    
    # Prorogue
    prorogue = fields.Boolean(string='Prorrogar')
    request_date = fields.Date(string='Fecha solicitud', default=fields.Date().today())
    prorogue_cause = fields.Text(string='Causa')
    prorogue_proposed_date = fields.Date(string='Fecha Propuesta')
    prorogue_approve = fields.Boolean(string='Aprobar')
    prorrogation_ids = fields.One2many(comodel_name='planning_turei.prorrogation', inverse_name='planning_slot_id', string='Prórrogas Aprobadas')
    
    # Attach information
    attach_file = fields.Binary(
        attachment=True,
        string="Archivo",
        copy=False,
    )
    attach_response = fields.Binary(
        attachment=True,
        string="Adjuntar Rpta.",
        copy=False,
    )
    # work_plan = fields.Boolean(string='Plan Trabajo', default=False)

    # -------------------------------------------------------------------------
    # INHERITED METHODS                                                       #
    # -------------------------------------------------------------------------
    def action_send(self):
        self.ensure_one()
        if not self.employee_id or not self.employee_id.work_email:
            self.state = 'published'
        employee_ids = self._get_employees_to_send_slot()
        
        # Add my registers
        if self.ejecutor_id:
            employee_ids |= self.ejecutor_id
        if self.control_compliance_id:
            employee_ids |= self.control_compliance_id
        
        self._send_slot(employee_ids, self.start_datetime, self.end_datetime)
        message = _("Tareas enviadas")
        return self._get_notification_action('success', message)

    def _send_slot(self, employee_ids, start_datetime, end_datetime, include_unassigned=True, message=None):
        if not include_unassigned:
            self = self.filtered(lambda s: s.resource_id)
        if not self:
            return False
        self.ensure_one()

        employee_with_backend = employee_ids.filtered(lambda e: e.user_id)
        employee_without_backend = employee_ids - employee_with_backend
        planning = False
        if employee_without_backend:
            planning = self.env['planning.planning'].create({
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'include_unassigned': include_unassigned,
            })

        template = self.env.ref('planning_turei.email_template_slot_single_modified')
        employee_url_map = {**employee_without_backend.sudo()._planning_get_url(planning), **employee_with_backend._slot_get_url(self)}

        cal_url = self._get_slot_resource_urls()
        cal_url['opermix_planning_url'] = 'https://intranet.turei.co.cu/odoo/planning' # Url del sistema opermix agregada
        view_context = dict(self._context)
        view_context.update({
            'open_shift_available': not self.employee_id,
            'mail_subject': _('Planificación: nuevo turno abierto disponible en'),
            'google_url': cal_url['google_url'],
            'iCal_url': cal_url['iCal'],
            'opermix_planning_url': cal_url['opermix_planning_url']
        })

        if self.employee_id:
            # employee_ids = self.employee_id # Comentar esta linea que impide el procesamiento para varios empleados
            if self.allow_self_unassign and not self.is_unassign_deadline_passed:
                if employee_ids.filtered(lambda e: e.user_id):
                    unavailable_link = '/planning/unassign/%s/%s' % (self.employee_id.sudo().employee_token, self.id)
                else:
                    unavailable_link = '/planning/%s/%s/unassign/%s?message=1' % (planning.access_token, self.employee_id.sudo().employee_token, self.id)
                view_context.update({'unavailable_link': unavailable_link})
            view_context.update({'mail_subject': _('Planificación: nueva tarea')})

        mails_to_send_ids = []
        for employee in employee_ids.filtered(lambda e: e.work_email):
            if not self.employee_id and employee in employee_with_backend and not self.is_past:
                view_context.update({'available_link': '/planning/assign/%s/%s' % (employee.sudo().employee_token, self.id)})
            elif not self.employee_id and not self.is_past:
                view_context.update({'available_link': '/planning/%s/%s/assign/%s?message=1' % (planning.access_token, employee.sudo().employee_token, self.id)})
            start_datetime = self._format_datetime_to_user_tz(self.start_datetime, employee.env, tz=employee.tz, lang_code=employee.user_partner_id.lang)
            end_datetime = self._format_datetime_to_user_tz(self.end_datetime, employee.env, tz=employee.tz, lang_code=employee.user_partner_id.lang)
            unassign_deadline = self._format_datetime_to_user_tz(self.unassign_deadline, employee.env, tz=employee.tz, lang_code=employee.user_partner_id.lang)
            allocated_hours = timedelta(hours=self.allocated_hours).total_seconds()
            formatted_allocated_hours = "%d:%02d" % (allocated_hours // 3600, round(allocated_hours % 3600 / 60))
            allocated_percentage = float_utils.float_repr(self.allocated_percentage, precision_digits=0)
            # update context to build a link for view in the slot
            view_context.update({
                'link': employee_url_map[employee.id],
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'employee_name': employee.name,
                'work_email': employee.work_email,
                'allocated_hours': formatted_allocated_hours,
                'allocated_percentage': allocated_percentage,
                'unassign_deadline': unassign_deadline
            })
            mail_id = template.with_context(view_context).send_mail(self.id, email_layout_xmlid='mail.mail_notification_light')
            mails_to_send_ids.append(mail_id)

        mails_to_send = self.env['mail.mail'].sudo().browse(mails_to_send_ids)
        if mails_to_send:
            mails_to_send.send()

        self.write({
            'state': 'published',
            'publication_warning': False,
        })

    @api.model_create_multi
    def create(self, vals):
        """Automatically generate a reference number for new tasks."""
        for val in vals:
            val['task_seq'] = self.env['ir.sequence'].next_by_code('planning.slot.task_seq')
        return super().create(vals)


    # -------------------------------------------------------------------------
    # COMPUTE METHODS                                                         #
    # -------------------------------------------------------------------------
    @api.depends("role_id")
    def _get_subcommissions_domain(self):
        for rec in self:
            if rec.role_id:
                rec.subcommissions_domain = [('planning_role_id', '=', rec.role_id.id)]
            else:
                rec.subcommissions_domain = []

    @api.onchange("role_id")
    def _onchange_role_id(self):
        if self.subcommissions_id.id is not self.role_id.id:
            self.subcommissions_id = False

    def _compute_controla_cumplimiento(self):
        for record in self:
            record.show_conformity = False
            if record.control_compliance_id:
                if record.control_compliance_id.id == self.env.user.id or self.env.user.has_group('planning.group_planning_manager'):
                    record.show_conformity = True
                else:
                    record.show_conformity = False

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS                                                        #
    # -------------------------------------------------------------------------
    @api.onchange('resource_id')
    def _onchange_resource_id(self):
        auxiliar = []
        if self.resource_id:
            for one in self.resource_id.employee_id.child_ids:
                auxiliar.append(one.id)
            auxiliar.append(self.resource_id.employee_id.id)
        self.child_ids = [(5, 0, False)]
        self.child_ids = self.env['hr.employee'].browse(auxiliar)

    @api.onchange('accomplished')
    def _onchange_accomplished(self):
        if self.accomplished:
            if not self.env.user.has_group('planning.group_planning_manager'):
                if self.env.user.id != self.ejecutor_id.user_id.id:
                    raise UserError(_('Usted no puede modificar el cumplimiento del Acuerdo, solo el Ejecutor puede hacerlo. '
                                      'Si cree que esto es un error contacte con su Administrador de Sistema.'))

    @api.onchange('prorogue_approve')
    def _onchange_prorogue_approve(self):
        if self.prorogue_approve:
            self.write({
                'prorrogation_ids': [(0, 0, {
                    'name': self.prorogue_cause,
                    'request_date': self.request_date,
                    'prorogue_proposed_date': self.prorogue_proposed_date,
                })]
            })
            self.prorogue = False
