from odoo import api, fields, models, tools
from odoo.tools.translate import _
from odoo.exceptions import UserError


class SmokeWzd(models.TransientModel):
    _name = "smoke.wzd"
    _description = "Smoke Wizard"

    def get_start_date(self):
        start_date, end_date = self.env["smoke.smoke"].get_date_range()
        return start_date

    def get_end_date(self):
        start_date, end_date = self.env["smoke.smoke"].get_date_range()
        return end_date

    start_date = fields.Date(
        string="Start Date",
        default=get_start_date,
    )

    end_date = fields.Date(
        string="End Date",
        default=get_end_date,
    )

    concept_id = fields.Many2one(
        string="Concept Relation",
        comodel_name="smoke.concept",
        ondelete="restrict",
    )

    def print_report(self):
        self.ensure_one()
        if self.end_date < self.start_date:
            raise UserError(_("Entrada incorrecta, el inicio es mayor que el fin"))
        datas = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "concept_id": self.concept_id.id,
        }
        print("DATA READ-------> ", datas)
        return self.env.ref("smoke.action_report_smoke").report_action(self, data=datas)
