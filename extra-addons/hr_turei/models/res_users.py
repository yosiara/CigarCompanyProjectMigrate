from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ResUsersExtended(models.Model):
    _inherit = 'res.users'

    def get_username(self):
        username = (self.login).split('@')[0].lower() if '@' in self.login else self.login
        return username
    
    def _find_matching_employee(self):
        """Buscar empleado existente para este usuario"""
        self.ensure_one()

        username = self.get_username()
        
        # 2. Buscar por username@dominio
        employee = self.env['hr.employee'].search([
            ('work_email', '=ilike', f'{username}@%'),
            ('user_id', '=', False)
        ], limit=1)

        return employee or False

    def _sync_employee(self, employee, employee_has_image=False):
        """Sincronizar datos del empleado al usuario"""
        self.ensure_one()
        
        sync_vals = {}
        
        # 1. Nombre (empleado → usuario)
        if employee.name and employee.name != self.name:
            sync_vals['name'] = employee.name
        
        # 2. Imagen (empleado → usuario)
        if employee_has_image and employee.image_1920 != self.image_1920:
            sync_vals['image_1920'] = employee.image_1920

        # 3. Work Phone (empleado → usuario)
        if employee.work_phone != self.phone:
            sync_vals['phone'] = employee.work_phone

        # 4. Mobile Phone (empleado → usuario)
        if employee.mobile_phone != self.mobile:
            sync_vals['mobile'] = employee.mobile_phone
        
        # 5. Work Email (empleado → usuario)
        if employee.work_email and employee.work_email != self.email:
            # username = (self.email).split('@')[0].lower()
            # sync_vals['login'] = username
            sync_vals['email'] = employee.work_email


        # 6. Job (empleado → usuario)
        if employee.job_id and employee.job_id.name != self.function:
            sync_vals['function'] = employee.job_id.name
        
        # 7. Active (empleado → usuario)
        if employee.active != self.active and not self._is_admin():
            sync_vals['active'] = employee.active

        # Retornar valores
        return sync_vals

    # def get_sync_employee_data(self, employee):
    #     """Devuelve valores para sincronizar desde empleado a usuario"""
    #     return {
    #         # 'create_employee_id': employee.id,
    #         'name': employee.name,
    #         'image_1920': employee.image_1920,
    #         'phone': employee.work_phone,
    #         'mobile': employee.mobile_phone,
    #         'email': employee.work_email,
    #         'function': employee.job_id.name,
    #         # 'partner_id': employee.work_contact_id.id,
    #         # 'login': (employee.work_email).split('@')[0].lower(),
    #     }

    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    # @api.model_create_multi
    # def create(self, vals_list):
    #     """Cuando se crea usuario, sincronizar datos desde empleado existente"""
    #     employee_by_login = {}
        
    #     for vals in vals_list:
    #         # Buscar empleado que coincida por login (email)
    #         login = vals.get('login')
    #         if login:
    #             employee = self._find_matching_employee(login)
    #             if employee:
    #                 # Sincronizar con empleado
    #                 employee_data = self.get_sync_employee_data(employee)
    #                 vals.update(**employee_data)
        
    #                 # Guardar referencia para vincular después
    #                 employee_by_login[login] = employee

    #     users = super(ResUsersExtended, self).create(vals_list)
        
    #     # Vincular empleados
    #     for user in users:
    #         employee_by_login[user.login].write({'user_id': user.id})
        
    #     return users

    @api.model_create_multi
    def create(self, vals_list):
        """Cuando se crea usuario, sincronizar empleado existente"""
        users = super(ResUsersExtended, self).create(vals_list)
        
        # Vincular empleados
        for user in users:
            employee = user._find_matching_employee()
            employee.write({'user_id': user.id})
        
        return users

    # ------------------------------------------------------------------------ #
    #                           ONCHANGE METHODS                               #
    # ------------------------------------------------------------------------ #

    # @api.onchange('email')
    # def _onchange_work_phone(self):
    #     if self.email:
    #         username = (self.email).split('@')[0].lower()
    #         if username != self.get_username():
    #             self.login = username

    # @api.onchange('employee_id.name')
    # def _onchange_name(self):
    #     if self.employee_id.name and self.employee_id.name != self.name:
    #         self.name = self.employee_id.name

    # @api.onchange('work_phone')
    # def _onchange_work_phone(self):
    #     if self.work_phone and self.work_phone != self.phone:
    #         self.phone = self.work_phone

    # @api.onchange('employee_id.image_1920')
    # def _onchange_image_1920(self):
    #     if self.employee_id.image_1920 and self.employee_id.image_1920 != self.image_1920:
    #         self.image_1920 = self.employee_id.image_1920

    # @api.onchange('employee_id.job_id')
    # def _onchange_job_id(self):
    #     if self.employee_id.job_id and self.employee_id.job_id.name != self.function:
    #         self.function = self.employee_id.job_id.name
        