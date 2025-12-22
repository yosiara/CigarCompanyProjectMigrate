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
            employee.image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            _logger.info(f"Foto asignada a '{employee.name}'")
        _logger.info(f"Fotos de empleados asignadas correctamente desde documentos!!!")
        return
        
    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            employee.image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
        return employees
    
    @api.model
    def write(self, vals):
        if 'registration_number' in vals: # Actualizar foto correspondiente
            vals['image_1920'] = self._get_photo_from_documents(registration_number=vals['registration_number'])
        res = super().write(vals)

        # Sincronizar datos para usuario, esto mantenerlo comentado hasta averiguar 
        # donde esta el metodo que cambia el nombre desde usuario hacia empleado
        # evitar sincronizacion circular
        # for employee in self:
        #     user = employee.user_id
        #     if user:
        #         user._sync_from_employee(employee)
                
        return res