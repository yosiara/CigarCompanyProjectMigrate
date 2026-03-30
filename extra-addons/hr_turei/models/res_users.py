from odoo import api, models, fields, _
import logging

_logger = logging.getLogger(__name__)

class ResUsersExtended(models.Model):
    _inherit = 'res.users'

    def get_username(self, login: str = False):
        if login:
            username = (login).split('@')[0].lower() if '@' in login else login
        else:
            self.ensure_one()
            username = (self.login).split('@')[0].lower() if '@' in self.login else self.login
        return username
    
    def _find_matching_employee(self, username: str):
        """ Buscar empleado para vinculación """
        
        # Buscar por username@dominio
        employee = self.env['hr.employee'].search([
            ('work_email', '=ilike', f'{username}@%'),
            ('work_contact_id', '!=', False),
            ('user_id', '=', False),
            ('active', '=', True),
        ], limit=1)

        if employee:
            return employee
        return False

    # ------------------------------------------------------------------------ #
    #                           OVERRIDE METHODS                               #
    # ------------------------------------------------------------------------ #

    @api.model_create_multi
    def create(self, vals_list):
        user_per_employee = {}
        for vals in vals_list:
            username = self.get_username(vals['login'])
            employee = self._find_matching_employee(username)

            if employee:
                partner_id = employee.work_contact_id
                sync_vals = {'partner_id': partner_id.id, **partner_id.read(employee.READ_PARTNER_FIELDS)[0]}
                vals.update(sync_vals)
                user_per_employee = {vals['login']: employee}

        users = super().create(vals_list)

        if user_per_employee:
            for user in users:
                employee = user_per_employee.get(user.login)
                if employee:
                    employee.user_id = user.id
        
        return users

    @api.model
    def default_get(self, fields):
        values = super(ResUsersExtended, self).default_get(fields)

        update_vals = {}
        
        langs = [code for code, _ in self.env['res.lang'].get_installed()]
        
        if 'es_ES' in langs:
            update_vals['lang'] = 'es_ES'

        update_vals['tz'] = 'America/Havana'

        if update_vals:
            values.update(update_vals)
        
        return values
        