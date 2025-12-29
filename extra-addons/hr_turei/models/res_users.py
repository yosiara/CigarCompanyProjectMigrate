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

    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        """Cuando se crea usuario, sincronizar empleado existente"""
        users = super(ResUsersExtended, self).create(vals_list)
        
        # Vincular empleados
        for user in users:
            employee = user._find_matching_employee()
            employee.write({'user_id': user.id})
        
        return users
        