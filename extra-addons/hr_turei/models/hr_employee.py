from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    planning_slot_id = fields.Many2one(comodel_name='planning.slot')
    
    def _assign_photo_from_documents(self, registration_number):
        """Busca y asigna la foto del empleado desde los documentos"""
        if not registration_number:
            return False
        document = self.env['documents.document'].search([
            ('mimetype', 'ilike', 'image/%'),   # Solo archivos de imagen
            ('name', '=ilike', f'{registration_number}.%')
        ], limit=1)
        if not document:
            return False # comodidad para filtros posteriores
        return document.datas # Obtener el contenido binario de la imagen

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            employee.image_1920 = self._assign_photo_from_documents(registration_number=employee.registration_number)
        return employees
    
    @api.model
    def write(self, vals):
        # Si se actualiza el código del empleado, buscar la foto
        if 'registration_number' in vals:
            vals['image_1920'] = self._assign_photo_from_documents(registration_number=vals['registration_number'])
        return super().write(vals)

    def action_assign_photo_from_documents(self):
        """Acción para asignar fotos desde documentos"""
        employees = self.search([])

        # Insertar foto para todos los empleados con codigo de trabajador
        for employee in employees:
            employee.image_1920 = self._assign_photo_from_documents(registration_number=employee.registration_number)

        _logger.info(f"Fotos de empleados asignadas desde documentos!!!")
        return