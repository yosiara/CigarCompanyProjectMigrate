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

    def _sync_to_users(self, user):
        """Sincronizar datos del empleado al usuario"""
        self.ensure_one()
        
        sync_vals = {}
        
        # 1. Nombre (empleado → usuario)
        if self.name != user.name:
            sync_vals['name'] = self.name
        
        # 2. Email (work_email → email)
        # if employee.work_email and self.email != employee.work_email:
        #     sync_vals['email'] = employee.work_email
        
        # 3. Timezone (si empleado tiene)
        if self.tz and self.tz != user.tz:
            sync_vals['tz'] = self.tz
        
        # 4. Imagen (empleado → usuario)
        # if employee.image_1920 and self.image_1920 != employee.image_1920:
        #     sync_vals['image_1920'] = employee.image_1920

        # 5. Partner (work_contact_id → partner_id)
        if self.work_contact_id and self.work_contact_id != user.partner_id:
            sync_vals['partner_id'] = self.work_contact_id
        
        # Archivar/Desarchivar usuario asociado, excluyendo administrador del sistema
        if self.active != user.active and user.id != user.env.ref('base.user_admin').id:
            sync_vals['active'] = self.active

        # Aplicar cambios al usuario
        if sync_vals:
            user.write(sync_vals)
        
        # 6. Sincronizar partner (contacto) del usuario
        # partner_vals = {}
        # if self.partner_id.name != employee.name:
        #     partner_vals['name'] = employee.name
        # if employee.work_email and self.partner_id.email != employee.work_email:
        #     partner_vals['email'] = employee.work_email
        
        # if partner_vals:
        #     self.partner_id.write(partner_vals)
        
        _logger.info(
            "Usuario %s sincronizado desde empleado %s (ID: %d)",
            user.login, self.name, self.id
        )
        
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

        # Probar si esto lo hace nativamente al asignarle un usuario
        # Sincronizar datos para usuario
        for employee in self:
            user = employee.user_id
            if user:
                employee._sync_to_users(user)
                
        return res