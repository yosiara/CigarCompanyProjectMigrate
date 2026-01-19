from odoo import models, fields, api, _
import logging
from datetime import timedelta
from odoo.tools import float_utils
from odoo.exceptions import UserError
from markupsafe import Markup

_logger = logging.getLogger(__name__)

class PlanningSlot(models.Model):
    _name = 'planning.slot'
    _inherit = ['planning.slot', 'mail.thread', 'mail.activity.mixin']
    _mail_post_access = 'read'

    # ------------------------------------------------------------------------ #
    #                           DEFAULT METHODS                                #
    # ------------------------------------------------------------------------ #
    def _default_next_task_seq(self):
        seq = self.env['ir.sequence'].search([('code', '=', 'planning.slot.task_seq')], limit=1)
        if not seq:
            return _("New")
        return seq.get_next_char(number_next=seq.number_next_actual)

    # General fields
    task_seq = fields.Char(string='N° Consecutivo', readonly=True, copy=False, index=True, default=_default_next_task_seq)
    subcommissions_id = fields.Many2one(comodel_name='planning_turei.subcommissions', string='Subcomisión', ondelete='cascade')
    agreement_number = fields.Char(string='N° Acuerdo')
    ejecutor_id = fields.Many2one(comodel_name='hr.employee', string='Ejecuta')
    
    # Prorogue fields
    show_prorogue = fields.Boolean(string='Prórroga')
    prorogation_ids = fields.One2many(comodel_name='planning_turei.prorogation', inverse_name='planning_slot_id', string='Prórrogas')

    # Compliance fields
    is_done = fields.Boolean(string='Cumplido')
    compliance_date = fields.Date(string='Fecha', default=fields.Date().today())
    compliance_info = fields.Text(string='Inf. Cumplimiento')
    control_compliance_id = fields.Many2one('hr.employee', string='Ctrl. Cumpl.')
    
    # Conformity fields
    show_conformity = fields.Boolean(string='Conformidad')
    final_verdict = fields.Selection([('completed', 'Completada'), ('not_completed', 'No completada'), ('revoked', 'Derogada')], string='Veredicto Final')
    conformity_date = fields.Date(string='Fecha', default=fields.Date().today())

    # Attach fields
    attach_file = fields.Binary(attachment=True, string="Adjuntar Archivo", copy=False)
    attach_response = fields.Binary(attachment=True, string="Adjuntar Rpta.", copy=False)

    # Domain fields
    ejecutor_domain = fields.Binary(compute="_get_ejecutor_domain", exportable=False)

    # closed_date = fields.Date(string='Fecha de Completada', default=fields.Date().today())
    # conformity = fields.Boolean(string='Conformidad')
    # compliance_real_show = fields.Boolean(string='Mostrar Fecha Real')
    # work_plan = fields.Boolean(string='Plan Trabajo', default=False)

    def get_notify_body(self, key: str):
        
        if key == "created":
            body = Markup(f"""
                <div style="font-family: Arial, sans-serif; padding: 15px; border-left: 4px solid #28a745; background-color: #f8f9fa;">
                    <h3 style="color: #28a745; margin-top: 0;">✅ Tarea Asignada</h3>
                    
                    <div style="margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>📋 Tarea:</strong> {self.task_seq or self.name}</p>
                        <p style="margin: 5px 0;"><strong>🙋‍♂️ Responsable:</strong> {self.resource_id.name}</p>
                        <p style="margin: 5px 0;"><strong>👤 Ejecutor:</strong> {self.ejecutor_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>🎯 Controlador:</strong> {self.control_compliance_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>✍️ Descripción:</strong> {self.name}</p>
                        <a href="{self.get_task_url()}" style="margin: 5px 0;"><strong>👁‍🗨 Abrir directamente</strong></a>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 10px; background-color: #e9ecef; border-radius: 5px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            <em>Este mensaje fue generado automáticamente cuando la tarea fue creada.</em>
                        </p>
                    </div>
                </div>
            """)

        elif key == "done":
            body = Markup(f"""
                <div style="font-family: Arial, sans-serif; padding: 15px; border-left: 4px solid #28a745; background-color: #f8f9fa;">
                    <h3 style="color: #28a745; margin-top: 0;">✅ Tarea Cumplida</h3>
                    
                    <div style="margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>📋 Tarea:</strong> {self.task_seq or self.name}</p>
                        <p style="margin: 5px 0;"><strong>🙋‍♂️ Responsable:</strong> {self.resource_id.name}</p>
                        <p style="margin: 5px 0;"><strong>👤 Ejecutor:</strong> {self.ejecutor_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>✍️ Descripción:</strong> {self.name}</p>
                        <p style="margin: 5px 0;"><strong>📅 Fecha de cumplimiento:</strong> {self.compliance_date or fields.Date.today()}</p>
                        <a href="{self.get_task_url()}" style="margin: 5px 0;"><strong>👁‍🗨 Abrir directamente</strong></a>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 10px; background-color: #e9ecef; border-radius: 5px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            <em>Este mensaje fue generado automáticamente cuando la tarea fue marcada como cumplida.</em>
                        </p>
                    </div>
                </div>
            """)
            # <p style="margin: 5px 0;"><strong>🎯 Controlador:</strong> {self.control_compliance_id.name}</p>

        return body

    def _send_is_done_notification(self):
        """Enviar notificación cuando una tarea es marcada como cumplida"""
        self.ensure_one()

        ctrl_compl = self.control_compliance_id
        if not ctrl_compl:
            msg = (f"No hay una persona asignada para controlar el cumplimiento de la tarea: {self.task_seq}")
            _logger.warning(msg)
            return

        user = ctrl_compl.user_id
        email = ctrl_compl.work_email
        subject=f'✅  Tarea Cumplida: {self.task_seq or self.name}'
        body = self.get_notify_body(key="done")

        if user:
            self.message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                partner_ids=[user.partner_id.id],
            )
        else:
            msg = f"{ctrl_compl.name} no tiene usuario asociado"
            _logger.warning(msg)

        if email:
            self._send_slot(employee_ids=ctrl_compl, start_datetime=self.start_datetime, end_datetime=self.end_datetime, mail_subject=subject)
        else:
            msg = f"{ctrl_compl.name} no tiene email asociado"
            _logger.warning(msg)

    def get_task_url(self):
        """Obtener la URL de la tarea"""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        return f"{base_url}/web#id={self.id}&model=planning.slot&view_type=form"

    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

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
        
        # Send notification by Odoo
        subject=f'📋  Tarea Creada: {self.task_seq or self.name}'
        body = self.get_notify_body(key="created")
        partner_ids = [
            employee.user_id.partner_id.id
            for employee in employee_ids
            if employee.user_id and employee.user_id.id != self.env.user.id
        ]
        self.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            partner_ids=partner_ids,
        )

        # Send notification by email
        self._send_slot(employee_ids, self.start_datetime, self.end_datetime, mail_subject=subject)
        
        message = _("Tareas enviadas")
        return self._get_notification_action('success', message)

    def _send_slot(self, employee_ids, start_datetime, end_datetime, include_unassigned=True, message=None, mail_subject: str = None): # Parametro agregado(mail_subject)
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

        template = self.env.ref('planning_turei.email_template_slot_single_modified') # Refencia a mi plantilla modificada
        employee_url_map = {**employee_without_backend.sudo()._planning_get_url(planning), **employee_with_backend._slot_get_url(self)}

        cal_url = self._get_slot_resource_urls()
        cal_url['opermix_planning_url'] = self.get_task_url() # Url del sistema opermix agregada
        view_context = dict(self._context)
        view_context.update({
            'open_shift_available': not self.employee_id,
            'mail_subject': mail_subject or _('Planificación: nuevo turno abierto disponible en'),
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
            view_context.update({'mail_subject': mail_subject or _('Planificación:  nueva tarea')})

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
    def create(self, vals_list):
        """Automatically generate a reference number for new tasks"""
        for vals in vals_list:
            vals['task_seq'] = self.env['ir.sequence'].next_by_code('planning.slot.task_seq') # Incrementar consecutivo
        return super().create(vals_list)

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if 'is_done' in vals and vals['is_done']:
            for rec in self:
                rec._send_is_done_notification()
        return res

    # ------------------------------------------------------------------------ #
    #                           COMPUTE METHODS                                #
    # ------------------------------------------------------------------------ #

    @api.depends("resource_id")
    def _get_ejecutor_domain(self):
        for rec in self:
            if rec.resource_id:
                rec.ejecutor_domain = [('id', 'in', (self.resource_id.employee_id.child_ids | self.resource_id.employee_id).ids)]
            else:
                rec.ejecutor_domain = [('id', 'in', False)]

    # def _compute_show_conformity(self):
    #     for record in self:
    #         record.show_conformity = False
    #         if record.control_compliance_id:
    #             if record.control_compliance_id.id == self.env.user.id or self.env.user.has_group('planning.group_planning_manager'):
    #                 record.show_conformity = True
    #             else:
    #                 record.show_conformity = False

    # ------------------------------------------------------------------------ #
    #                           ONCHANGE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.onchange("role_id")
    def _onchange_role_id(self):
        if self.subcommissions_id.planning_role_id.id is not self.role_id.id:
            self.subcommissions_id = False

    @api.onchange("resource_id")
    def _onchange_resource_id(self):
        if self.ejecutor_id not in self.resource_id.employee_id.child_ids | self.resource_id.employee_id:
            self.ejecutor_id = False

    # @api.onchange('is_done')
    # def _onchange_is_done(self):
    #     if self.is_done:
    #         if not self.env.user.has_group('planning.group_planning_manager'):
    #             if self.env.user.id != self.ejecutor_id.user_id.id:
    #                 raise UserError(_('Usted no puede modificar el cumplimiento del Acuerdo, solo el Ejecutor puede hacerlo. '
    #                                   'Si cree que esto es un error contacte con su Administrador de Sistema.'))


class PlanningRole(models.Model):
    _inherit = 'planning.role'

    management_book = fields.Boolean('Libro de la Gestión')