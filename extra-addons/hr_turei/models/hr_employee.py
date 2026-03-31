from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class HREmployee(models.Model):
    _inherit = 'hr.employee'

    @property
    def READ_PARTNER_FIELDS(self):
        """ Get fields for partner """
        return [v[1] for _, v in self.MAPPED_EMPLOYEE_PARTNER_FIELDS.items()]

    @property
    def READ_FIELDS(self):
        """ Get fields for employee """
        return [v[0] for _, v in self.MAPPED_EMPLOYEE_PARTNER_FIELDS.items()]

    @property
    def MAPPED_EMPLOYEE_PARTNER_FIELDS(self):
        """ Mapeo de campos no computados que sincronizarán contacto """
        return {
            'name': ('name', 'name'),
            'email': ('work_email', 'email'),
            'mobile': ('mobile_phone', 'mobile'),
            'phone': ('work_phone', 'phone'),
            'job_title': ('job_title', 'function'),
            'image': ('image_1920', 'image_1920'),
            'lang': ('lang', 'lang'),
            'tz': ('tz', 'tz'),
        }

    def _sync_partner(self, e_vals: dict, p_vals: dict):
        """ Sincronizar contacto """
        sync_vals = {}

        for k, v in self.MAPPED_EMPLOYEE_PARTNER_FIELDS.items():
            e_field, p_field = v
            if e_field not in e_vals or p_field not in p_vals:
                continue
            
            e_value = e_vals[e_field]
            p_value = p_vals[p_field]
            
            if k in ['image'] and not e_value: # Excluir valores vacios
                continue

            if e_value != p_value:
                sync_vals[p_field] = e_value 
        
        return sync_vals

    def _get_photo_from_documents(self, registration_number):
        """ Obtener la foto del empleado desde documentos """
        if not registration_number:
            return False
        document = self.env['documents.document'].search([
            ('mimetype', 'ilike', 'image/%'),   # Solo archivos de imagen
            ('name', '=ilike', f'{registration_number}.%')
        ], limit=1)
        if not document:
            return False # Comodidad para filtros posteriores
        return document.datas

    def _action_prepare_data(self):
        """
        Sincronización completa:
        1. Asignar foto desde documentos
        2. Configurar idioma y zona horaria
        3. Vincular usuarios
        4. Sincronizar datos con partners
        """
        _logger.info("========== INICIANDO SINCRONIZACIÓN DE EMPLEADOS ==========")
        
        employees = self.search([])
        users = self.user_id.search([])
        users_list = list(users)

        success_count = 0
        error_count = 0

        for employee in employees:
            try:
                _logger.info(f"-->> Procesando empleado: {employee.name} (Código: {employee.registration_number or 'Sin código'})")

                e_vals = employee.read(employee.READ_FIELDS)[0]
                update_vals = {}

                # 1. Asignar foto desde documentos
                image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
                if image_1920 != employee.image_1920:
                    update_vals['image_1920'] = image_1920
                    _logger.info(f"---->> Foto actualizada")

                # 2. Configuración regional específica para Cuba
                if employee.lang != 'es_ES':
                    update_vals['lang'] = 'es_ES'
                    _logger.info(f"---->> Idioma actualizado a Spanish/Español")
                if employee.tz != 'America/Havana':
                    update_vals['tz'] = 'America/Havana'
                    _logger.info(f"---->> Zona horaria actualizada a America/Havana")
                
                # 3. Vincular usuario si tiene email y no tiene usuario asignado
                if employee.work_email and not employee.user_id:
                    username = employee.work_email.split('@')[0].lower()
                    for i, user in enumerate(users_list):
                        if user.login == username:
                            update_vals['user_id'] = user.id
                            _logger.info(f"--->> Usuario vinculado: {user.login}")
                            del users_list[i]
                            break
                
                if update_vals:
                    employee.write(update_vals)
                    e_vals.update(update_vals)
                
                # 4. Sincronizar datos con el partner
                partner = employee.work_contact_id
                p_vals = partner.read(employee.READ_PARTNER_FIELDS)[0]
                sync_partner = employee._sync_partner(e_vals, p_vals)
                
                if sync_partner:
                    partner.write(sync_partner)
                    _logger.info(f'---->> Contacto sincronizado')

                success_count += 1

            except Exception as e:
                error_count += 1
                _logger.error(f"ERROR procesando empleado {employee.name}: {str(e)}")

        # Resumen final
        _logger.info("========== SINCRONIZACIÓN COMPLETADA ==========")
        _logger.info(f"Empleados procesados: {success_count}")
        _logger.info(f"Errores: {error_count}")

        return
        
    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    def _remove_work_contact_id(self, user, employee_company):
        """ Remove work_contact_id for previous employee if the user is assigned to a new employee """
        employee_company = employee_company or self.company_id.id
        # For employees with a user_id, the constraint (user can't be linked to multiple employees) is triggered
        old_partner_employee_ids = user.partner_id.employee_ids.filtered(lambda e:
            not e.user_id
            and e.company_id.id == employee_company
            and e != self
        )
        without_user_partner_ids = old_partner_employee_ids.filtered(lambda e: e.work_contact_id and e.work_contact_id.user_ids == False)
        old_partner_employee_ids.work_contact_id = None # Desvincular partner
        if without_user_partner_ids:
            without_user_partner_ids.active = False # Archivar partner
            _logger.warning(f"Archived work contacts: {without_user_partner_ids.mapped('name')}")

    @api.model_create_multi
    def create(self, vals_list):
        employees = super().create(vals_list)
        for employee in employees:
            image_1920 = self._get_photo_from_documents(registration_number=employee.registration_number)
            if image_1920 != employee.image_1920:
                employee.image_1920 = image_1920
        return employees

    def write(self, vals):
        res = super().write(vals)

        if any(field in vals for field in self.READ_FIELDS):
            for employee in self:
                if employee.work_contact_id:
                    partner = employee.work_contact_id
                    p_vals = partner.read(employee.READ_PARTNER_FIELDS)[0]
                    sync_vals = employee._sync_partner(vals, p_vals)
                    if sync_vals:
                        partner.write(sync_vals)
        
        return res

    # ------------------------------------------------------------------------ #
    #                           ONCHANGE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.onchange('registration_number')
    def _onchange_registration_number(self):
        image_1920 = self._get_photo_from_documents(registration_number=self.registration_number)
        if image_1920 != self.image_1920:
            self.image_1920 = image_1920