from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ResUsersExtended(models.Model):
    _inherit = 'res.users'
    
    def _find_matching_employee(self):
        """Buscar empleado existente para este usuario"""
        self.ensure_one()
        username = (self.login).split('@')[0].lower() if '@' in self.login else self.login
        
        # 2. Buscar por username@dominio
        employee = self.env['hr.employee'].search([
            ('work_email', '=ilike', f'{username}@%'),
            ('user_id', '=', False)
        ], limit=1)

        return employee or False

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
        