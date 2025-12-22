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

    def _sync_from_employee(self, employee):
        """Sincronizar datos del empleado al usuario"""
        self.ensure_one()
        
        sync_vals = {}
        
        # 1. Nombre (empleado → usuario)
        if self.name != employee.name:
            sync_vals['name'] = employee.name
        
        # 4. Imagen (empleado → usuario)
        if employee.image_1920 and self.image_1920 != employee.image_1920:
            sync_vals['image_1920'] = employee.image_1920
        
        # Archivar/Desarchivar usuario asociado, excluyendo administrador del sistema
        if employee.active != self.active and not self._is_admin():
            sync_vals['active'] = employee.active

        # Aplicar cambios al usuario
        if sync_vals:
            self.write(sync_vals)

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
                # 1. Sincronizar datos no compartidos
                user._sync_from_employee(employee)

                # 2. Partner (work_contact_id → partner_id)
                if employee.work_contact_id and user.partner_id != employee.work_contact_id:
                    user.partner_id.write(employee.work_contact_id)
                
                # 3. Vincular empleado con usuario
                employee.write({'user_id': user.id})
        
        return users