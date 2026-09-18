from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    @api.constrains('resource_type')
    def _check_type(self):
        for resource in self:
            if resource.resource_type == 'user' and not self.env.user.has_group('hr.group_hr_user'):
                raise ValidationError(_('Only those responsible for managing employees can create human resources.'))