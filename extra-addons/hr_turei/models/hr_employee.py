from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_photo_from_documents(self, registration_number):
        """Busca la foto del empleado en documentos"""
        if not registration_number:
            return False
        document = self.env['documents.document'].search([
            ('mimetype', 'ilike', 'image/%'),   # Solo archivos de imagen
            ('name', '=ilike', f'{registration_number}.%')
        ], limit=1)
        if not document:
            return False # comodidad para filtros posteriores
        return document.datas # Obtener el contenido binario de la imagen

    def action_assign_photo_from_documents(self):
        """Acción para asignar foto a todos los empleados desde documentos"""
        employees = self.search([])

        # Insertar foto para todos los empleados con codigo de trabajador
        for employee in employees:
            image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            if image_1920 != employee.image_1920:
                employee.image_1920 = image_1920
                _logger.info(f"Foto asignada a '{employee.name}'")

        message = "Fotos de empleados asignadas correctamente desde documentos!!!"
        _logger.info(message)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': message,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
        
    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            if image_1920 != employee.image_1920:
                employee.image_1920 = image_1920
        return employees

    # ------------------------------------------------------------------------ #
    #                           ONCHANGE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.onchange('name', 'user_id')
    def _onchange_name(self):
        if self.name and self.user_id and self.name != self.user_id.name:
            self.user_id.name = self.name

    @api.onchange('work_phone', 'user_id')
    def _onchange_work_phone(self):
        if self.work_phone and self.user_id and self.work_phone != self.user_id.phone:
            self.user_id.phone = self.work_phone

    @api.onchange('image_1920', 'user_id')
    def _onchange_image_1920(self):
        if self.image_1920 and self.user_id and self.image_1920 != self.user_id.image_1920:
            self.user_id.image_1920 = self.image_1920

    @api.onchange('job_id', 'user_id')
    def _onchange_job_id(self):
        if self.job_id and self.user_id and self.job_id.name != self.user_id.function:
            self.user_id.function = self.job_id.name

    @api.onchange('registration_number')
    def _onchange_registration_number(self):
        image_1920 = self._get_photo_from_documents(registration_number=self.registration_number)
        if image_1920 != self.image_1920:
            self.image_1920 = image_1920