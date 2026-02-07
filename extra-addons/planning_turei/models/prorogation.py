from odoo import models, fields, api, _
from markupsafe import Markup

import logging
_logger = logging.getLogger(__name__)
class Prorogation(models.Model):
    _name = 'planning_turei.prorogation'
    _description = 'Planning Turei Prorogation'
    
    request_date = fields.Date(string='Fecha Solicitada', default=fields.Date().today(), readonly=True) # Campo posiblemente inncesario
    cause = fields.Text(string='Causa', required=True)
    proposed_date = fields.Date(string='Fecha Propuesta')
    is_approved = fields.Boolean(string='Aprobar')
    planning_slot_id = fields.Many2one('planning.slot')

    def get_prorogation_body(self, key: str):
        if key == "prorogue":
            body = Markup(f"""
                <div style="font-family: Arial, sans-serif; padding: 15px; border-left: 4px solid #28a745; background-color: #f8f9fa;">
                    <h3 style="color: #28a745; margin-top: 0;">⏳ Tarea: solicitud de prórroga</h3>
                    
                    <div style="margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>#️⃣ Número:</strong> {self.planning_slot_id.task_seq}</p>
                        <p style="margin: 5px 0;"><strong>🙋‍♂️ Responsable:</strong> {self.planning_slot_id.resource_id.name}</p>
                        <p style="margin: 5px 0;"><strong>👤 Ejecutor:</strong> {self.planning_slot_id.ejecutor_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>🎯 Controlador:</strong> {self.planning_slot_id.control_compliance_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>✍️ Descripción:</strong> {self.planning_slot_id.name}</p>
                        <p style="margin: 5px 0;"><strong>🔍 Causa:</strong> {self.cause}</p>
                        <p style="margin: 5px 0;"><strong>📅 Fecha Propuesta:</strong> {self.proposed_date or 'Sin sugerencia'}</p>
                        <a href="{self.get_task_url()}" style="margin: 5px 0;"><strong>👁‍🗨 Abrir directamente</strong></a>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 10px; background-color: #e9ecef; border-radius: 5px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            <em>Este mensaje fue generado automáticamente cuando fue solicitada una prórroga para esta tarea.</em>
                        </p>
                    </div>
                </div>
            """)
        elif key == "approved":
            body = Markup(f"""
                <div style="font-family: Arial, sans-serif; padding: 15px; border-left: 4px solid #28a745; background-color: #f8f9fa;">
                    <h3 style="color: #28a745; margin-top: 0;">🔄 Tarea: solicitud de prórroga</h3>
                    
                    <div style="margin: 15px 0;">
                        <p style="margin: 5px 0;"><strong>#️⃣ Número:</strong> {self.planning_slot_id.task_seq}</p>
                        <p style="margin: 5px 0;"><strong>🙋‍♂️ Responsable:</strong> {self.planning_slot_id.resource_id.name}</p>
                        <p style="margin: 5px 0;"><strong>👤 Ejecutor:</strong> {self.planning_slot_id.ejecutor_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>🎯 Controlador:</strong> {self.planning_slot_id.control_compliance_id.name or 'No asignado'}</p>
                        <p style="margin: 5px 0;"><strong>✍️ Descripción:</strong> {self.planning_slot_id.name}</p>
                        <p style="margin: 5px 0;"><strong>🔍 Causa:</strong> {self.cause}</p>
                        <p style="margin: 5px 0;"><strong>📅 Fecha Propuesta:</strong> {self.proposed_date or 'Sin sugerencia'}</p>
                        <p style="margin: 5px 0;"><strong>✔️ Aprobada por:</strong> {self.planning_slot_id.create_uid.name or 'Persona anónima'}</p>
                        <a href="{self.get_task_url()}" style="margin: 5px 0;"><strong>👁‍🗨 Abrir directamente</strong></a>
                    </div>
                    
                    <div style="margin-top: 15px; padding: 10px; background-color: #e9ecef; border-radius: 5px;">
                        <p style="margin: 0; font-size: 12px; color: #666;">
                            <em>Este mensaje fue generado automáticamente cuando fue aprobada la solicitud de prórroga para esta tarea.</em>
                        </p>
                    </div>
                </div>
            """)
        return body

    def _send_request_notification(self):
        """ Enviar notificación al creador de la tarea cuando se solicita una prórroga """
        self.ensure_one()

        owner = self.create_uid

        # Send notification by Odoo
        subject=f'⏳ Solicitud de prórroga. Tarea: {self.planning_slot_id.task_seq}'
        body = self.get_prorogation_body(key="prorogue")
        self.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_note',
            partner_ids=[owner.partner_id.id],
        )
        # Send notification by email
        if owner.email:
            self.planning_slot_id._send_slot(employee_ids=owner.employee_ids, start_datetime=self.planning_slot_id.start_datetime, end_datetime=self.planning_slot_id.end_datetime, mail_subject=subject)
        else:
            msg = f"{owner.name} no tiene email asociado"
            _logger.warning(msg)

    def _send_approved_notification(self):
        """ Enviar notificación al responsable de la tarea cuando es aprobada una prórroga """
        self.ensure_one()

        responsable = self.resource_id.employee_id

        # Send notification by Odoo
        subject=f'🔄 Aprobación de prórroga. Tarea: {self.planning_slot_id.task_seq}'
        body = self.get_prorogation_body(key="approved")
        if responsable.user_id:
            self.message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_note',
                partner_ids=[responsable.user_id.partner_id.id],
            )
        # Send notification by email
        if responsable.email:
            self.planning_slot_id._send_slot(employee_ids=responsable, start_datetime=self.planning_slot_id.start_datetime, end_datetime=self.planning_slot_id.end_datetime, mail_subject=subject)
        else:
            msg = f"{responsable.name} no tiene email asociado"
            _logger.warning(msg)

    @api.model_create_multi
    def create(self, vals_list):
        prorogations = super().create(vals_list)
        for p in prorogations:
            p._send_request_notification()
        return prorogations

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if 'is_approved' in vals and vals['is_approved']:
            for rec in self:
                rec._send_approved_notification()
        return res
    
    # @api.onchange('prorogue_approve')
    # def _onchange_prorogue_approve(self):
    #     if self.prorogue_approve:
    #         self.write({
    #             'prorrogation_ids': [(0, 0, {
    #                 'name': self.prorogue_cause,
    #                 'request_date': self.request_date,
    #                 'prorogue_proposed_date': self.prorogue_proposed_date,
    #             })]
    #         })
    #         self.prorogue = False