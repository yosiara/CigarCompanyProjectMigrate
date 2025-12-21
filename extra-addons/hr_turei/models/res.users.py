from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ResUsersExtended(models.Model):
    _inherit = 'res.users'
    
    def _find_matching_employee(self):
        """Buscar empleado existente para este usuario"""
        self.ensure_one()

        username = self.login.split('@')[0].lower() if '@' in self.login else self.login
        
        # 2. Buscar por username@dominio
        employee = self.env['hr.employee'].search([
            ('work_email', '=ilike', f'{username}@%'),
            ('user_id', '=', False)
        ], limit=1)

        return employee or False

    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        """Cuando se crea usuario desde LDAP, sincronizar datos desde empleado existente"""
        users = super(ResUsersExtended, self).create(vals_list)
        
        for user in users:
            # Buscar empleado que coincida
            employee = user._find_matching_employee()
            if employee:
                # Vincular empleado con usuario
                employee.write({'user_id': user.id})
        
        return users
    
    # def write(self, vals):
    #     """Sobreescribir write para manejar sincronización bidireccional"""
    #     # Primero guardar cambios en usuario
    #     result = super(ResUsersExtended, self).write(vals)
        
    #     # Si el usuario tiene empleado vinculado, propagar CIERTOS cambios
    #     for user in self:
    #         if user.employee_ids:
    #             employee = user.employee_ids[0]
                
    #             # Solo propagar cambios que NO afecten datos principales del empleado
    #             # Por ejemplo: tz, imagen, pero NO nombre ni email
    #             emp_vals = {}
                
    #             # Timezone (usuario puede actualizar su tz)
    #             if 'tz' in vals and employee.tz != user.tz:
    #                 emp_vals['tz'] = user.tz
                
    #             # Imagen (usuario puede cambiar su avatar)
    #             if 'image_1920' in vals and employee.image_1920 != user.image_1920:
    #                 emp_vals['image_1920'] = user.image_1920
    #                 if employee.work_contact_id:
    #                     employee.work_contact_id.image_1920 = user.image_1920
                
    #             if emp_vals:
    #                 employee.write(emp_vals)
        
    #     return result