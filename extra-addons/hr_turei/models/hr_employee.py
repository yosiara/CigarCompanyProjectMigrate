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
        return document.datas

    def _action_prepare_data(self):
        """
        Cambiar el idioma de todos los contactos al Español y zona horaria de Cuba.
        Archivar contactos huerfanos.
        Asignar foto desde documentos a los empleados según código de trabajor.
        Sincronizar usuarios, información primaria manejada desde empleados.
        """

        _logger.info(f"# ------------ Procesando Contactos ------------ #")
        partners = self.env['res.partner'].search([])
        for partner in partners:
            _logger.info(f"-->> Contacto {partner.name}...")
            partner_vals = {}
            
            if partner.lang != 'es_ES': # Usar lenguaje Español
                partner_vals['lang'] = 'es_ES'
                _logger.info(f"---->> Lenguaje actualizado a Spanish/Español")
            if partner.tz != 'America/Havana': # Usar zona horaria de Cuba
                partner_vals['tz'] = 'America/Havana'
                _logger.info(f"---->> Zona horaria actualizada a America/Havana")
            if partner.employee_ids == False and partner.user_ids == False and partner.id >= 8: # Archivar contactos huerfanos
                partner_vals['active'] = False
                _logger.info(f"---->> Registro huerfano archivado: ID={partner.id}")
            if partner_vals:
                partners.write(partner_vals)

        _logger.info(f"# ------------ Procesando Empleados ------------ #")
        employees = self.search([])
        users = list(self.user_id.search([]))
        for employee in employees:
            _logger.info(f"-->> Empleado {employee.name}...")
            sync_employee = {}

            # Buscar foto de empleado por código de trabajador
            image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            if image_1920 != employee.image_1920:
                sync_employee['image_1920'] = image_1920
                _logger.info(f"---->> Foto actualizada")
            
            # Buscar usuario, sincronizar y vincular
            username = (employee.work_email).split('@')[0].lower() if employee.work_email else False
            if username:
                for i, user in enumerate(users):
                    if user.login == username:
                        sync_user = user._sync_employee(employee)
                        if sync_user:
                            user.write(sync_user)
                            _logger.info(f"---->> Usuario sincronizado")
                        if not employee.user_id:
                            sync_employee['user_id'] = user.id
                            _logger.info(f"---->> Usuario asignado: ID={user.id}")
                        del users[i]
                        break
            
            # Aplicar cambios a empleado
            if sync_employee:
                employee.write(sync_employee)

        return
        
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

    @api.onchange('registration_number')
    def _onchange_registration_number(self):
        image_1920 = self._get_photo_from_documents(registration_number=self.registration_number)
        if image_1920 != self.image_1920:
            self.image_1920 = image_1920

    """ Sincronizar datos del empleado al usuario """
    @api.onchange('name')
    def _onchange_name(self):
        # 1. Name (empleado → usuario)
        if self.name and self.user_id and self.name != self.user_id.name:
            self.user_id.name = self.name

    @api.onchange('image_1920')
    def _onchange_image_1920(self):
        # 2. Image (empleado → usuario)
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

    # No se ejecuta al archivar
    # @api.onchange('active')
    # def _onchange_active(self):
    #     # 5. Active (empleado → usuario)
    #     _logger.info(f"----------->> Inside Self: {self}")
    #     if self.user_id and not self.user_id._is_admin() and self.active != self.user_id.active:
    #         self.user_id.active = self.active