from odoo import api, fields, models, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class CycleMaintenancePlan(models.Model):
    _name = "maintenance_turei.cycle_maintenance_plan"
    _description = 'Cycle Maintenance Plan'
    _rec_name = 'cycle'

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
                                   ondelete='cascade')
    cycle = fields.Many2one('maintenance_turei.cycle_maintenance', string='Ciclo', domain="[('equipment_id', '=', equipment_id)]")

    date = fields.Date('Fecha Inicio')
    year_char = fields.Char(string=u"Año", required=False, compute="_compute_year_char", store=True)

    @api.depends('date')
    def _compute_year_char(self):
        for c_model in self:
            if c_model.date:
                date = fields.datetime #.strptime(c_model.date, DEFAULT_SERVER_DATE_FORMAT)
                c_model.year_char = str(date.year)

    @api.model
    def create(self, vals):
        res = super(CycleMaintenancePlan, self).create(vals)
        res.equipment_id._create_new_request(res.date, res.cycle)
        return res

    @api.model_create_multi
    def unlink(self):
        self.env['maintenance.request'].search([('equipment_id', '=', self.equipment_id.id), ('cycle_id', '=', self.cycle.id), ('request_date', '=', self.date)]).unlink()
        return super(CycleMaintenancePlan, self).unlink()
