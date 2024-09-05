from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError


class SmokeWzd(models.TransientModel):
    _name = "smoke.wzd"
    _description = "Smoke Wizard"

    start_date = fields.Date(
        string="Start Date",
        default=fields.Date.context_today,
    )

    end_date = fields.Date(
        string="End Date",
        default=fields.Date.context_today,
    )

    def print_report(self):
        self.ensure_one()
        if self.end_date < self.start_date:
            raise UserError(_("Entrada incorrecta, el inicio es mayor que el fin"))
        datas = {
            "start_date": self.start_date,
            "end_date": self.end_date,
        }
        print("DATA READ-------> ", datas)
        return self.env.ref("smoke.action_report_smoke").report_action(self, data=datas)
