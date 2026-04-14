# -*- coding: utf-8 -*-

from odoo import api, models, fields


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    short_name = fields.Char('Short name', help='Department short name.')
    is_productive = fields.Boolean('Is productive?', help='Check this box if department is productive.')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = ''
            if record.short_name:
                name = record.short_name
            else:
                name = record.name
            if record.parent_id:
                name = "%s / %s" % (record.parent_id.name_get()[0][1], name)
            result.append((record.id, name))
        return result
