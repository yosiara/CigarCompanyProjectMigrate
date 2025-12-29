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

    def action_assign_photo_and_sync_user(self):
        """Acción para asignar foto a todos los empleados desde documentos"""
        employees = self.search([])

        count_images = 0
        count_sync_user = 0
        for employee in employees:
            # Buscar e insertar foto para empleado con código de trabajador
            image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            if image_1920 != employee.image_1920:
                employee.image_1920 = image_1920
                _logger.info(f"---->> Foto asignada al empleado: {employee.name}")
                count_images += 1
            
            # Buscar matching con usuario, syncronizar y vincular
            username = (employee.work_email).split('@')[0]
            user = self.env['res.users'].search([('login', '=', username)], limit=1)
            if user and not employee.user_id:
                employee.user_id = user.id
                _logger.info(f"---->> Usuario con ID = {user.id} sincronizado y vinculado a {employee.name}")
                count_sync_user += 1


        message = (f"---->> Asignadas {count_images} fotos"
                   f"---->> Sincronizados {count_sync_user} usuarios"
        )
        _logger.info(message)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'type': 'success',
                'message': message,
                # 'next': {'type': 'ir.actions.act_window_close'},
            }
        }
        
    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.onchange('user_id')
    def _onchange_user(self):
        # self.update(self._sync_user(self.user_id, (bool(self.image_1920))))
        # if not self.name:
        #     self.name = self.user_id.name
        pass

    # def _sync_user(self, user, employee_has_image=False):
    #     sync_vals = {}

    #     # Sincronizar usuario, priorizar la siguiente información del empleado, antes del vínculo
    #     if self.name != user.name:
    #         sync_vals['name'] = self.name
    #     if employee_has_image and self.image_1920 != user.image_1920:
    #         sync_vals['image_1920'] = self.image_1920
    #     if self.work_phone != user.phone:
    #         sync_vals['phone'] = self.work_phone
    #     if self.mobile_phone != user.mobile:
    #         sync_vals['mobile'] = self.mobile_phone
    #     if self.work_email != user.email:
    #         sync_vals['email'] = self.work_email
    #     if self.job_id and self.job_id.name != user.function:
    #         sync_vals['function'] = self.job_id.name
    #     if sync_vals:
    #         user.write(**sync_vals)
        
    #     vals = dict(
    #         work_contact_id=user.partner_id.id if user else self.work_contact_id.id,
    #         user_id=user.id,
    #     )
    #     # if not employee_has_image:
    #     #     vals['image_1920'] = user.image_1920
    #     if user.tz:
    #         vals['tz'] = user.tz
    #     return vals

    def _sync_user(self, user, employee_has_image=False):
        """Sincronizar usuario antes del vínculo, priorizar información del empleado"""
        vals = user._sync_employee(employee=self, employee_has_image=employee_has_image)
        if vals:
            user.write(**vals)
        
        vals = dict(
            work_contact_id=user.partner_id.id if user else self.work_contact_id.id,
            user_id=user.id,
        )
        # if not employee_has_image:
        #     vals['image_1920'] = user.image_1920
        if user.tz:
            vals['tz'] = user.tz
        return vals

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

    @api.onchange('registration_number')
    def _onchange_registration_number(self):
        image_1920 = self._get_photo_from_documents(registration_number=self.registration_number)
        if image_1920 != self.image_1920:
            self.image_1920 = image_1920

    """ Sincronizar datos del empleado al usuario """
    @api.onchange('name')
    def _onchange_name(self):
        # 1. Nombre (empleado → usuario)
        if self.name and self.user_id and self.name != self.user_id.name:
            self.user_id.name = self.name

    @api.onchange('image_1920')
    def _onchange_image_1920(self):
        # 2. Imagen (empleado → usuario)
        if self.image_1920 and self.user_id and self.image_1920 != self.user_id.image_1920:
            self.user_id.image_1920 = self.image_1920
    
    @api.onchange('work_phone')
    def _onchange_work_phone(self):
        # 3. Work Phone (empleado → usuario)
        if self.work_phone and self.user_id and self.work_phone != self.user_id.phone:
            self.user_id.phone = self.work_phone

    @api.onchange('job_id')
    def _onchange_job_id(self):
        # 4. Job (empleado → usuario)
        if self.job_id and self.user_id and self.job_id.name != self.user_id.function:
            self.user_id.function = self.job_id.name

    @api.onchange('active')
    def _onchange_job_id(self):
        # 5. Active (empleado → usuario)
        if self.user_id and not self.user_id._is_admin() and self.active != self.user_id.active:
            self.user_id.active = self.active