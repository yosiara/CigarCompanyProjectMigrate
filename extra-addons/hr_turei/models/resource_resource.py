from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ResourceResource(models.Model):
    _inherit = "resource.resource"

    @api.constrains('resource_type')
    def _check_type(self):
        for resource in self:
            if resource.resource_type == 'user' and not self.env.user.has_group('hr.group_hr_user'):
                raise ValidationError('Solo los encargados de gestionar empleados pueden crear recursos de tipo humano')