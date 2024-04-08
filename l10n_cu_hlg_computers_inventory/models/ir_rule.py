from odoo import fields, models, api


class IrRule (models.Model):
    _inherit = 'ir.rule'

    @api.model
    def _eval_context(self):
        """Returns a dictionary to use as evaluation context for
           ir.rule domains."""
        res = super(IrRule, self)._eval_context()
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.user.id)], limit=1)
        res['employee'] = employee if employee else False
        return res
    


