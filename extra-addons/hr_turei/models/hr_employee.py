from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    planning_slot_id = fields.Many2one('planning.slot')
    
    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        
        for employee in employees:
            employee._assign_photo_from_documents()

        return employees
    
    @api.model
    def write(self, vals):
        result = super().write(vals)
        
        # Si se actualiza el código del empleado, buscar la foto
        if 'registration_number' in vals:
            for employee in self:
                employee._assign_photo_from_documents()
        
        return result
    
    def _assign_photo_from_documents(self):
        """Busca y asigna la foto del empleado desde los documentos"""
        self.ensure_one()
        
        if not self.registration_number:
            self.image_1920 = False # comodidad para filtros posteriores
            return
        
        document = self.env['documents.document'].search([
            ('mimetype', 'ilike', 'image/%'),
            ('name', '=ilike', f'{self.registration_number}.%')
        ], limit=1) # Solo archivos de imagen

        if document:
            image_data = document.datas # Obtener el contenido binario de la imagen
            try:
                self.image_1920 = image_data
                _logger.info(f"Foto asignada automáticamente para empleado {self.registration_number}")
            except Exception as e:
                _logger.error(f"Error al asignar foto para empleado {self.registration_number}: {str(e)}")
        else:
            self.image_1920 = False # comodidad para filtros posteriores
        

    def action_assign_photo_from_documents(self):
        """Acción para asignar fotos desde documentos"""
        employees = self.search([])

        # Insertar foto para todos los empleados con codigo de trabajador
        for employee in employees:
            employee._assign_photo_from_documents()

        _logger.info(f"Se asignaron todas las fotos desde documentos")
        return