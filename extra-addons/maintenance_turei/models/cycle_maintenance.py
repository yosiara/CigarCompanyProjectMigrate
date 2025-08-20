from odoo import api, fields, models, tools, _

class CycleMaintenance(models.Model):
    _name = "maintenance_turei.cycle_maintenance"
    _description = 'Cycle Maintenance'
    _rec_name = 'cycle'

    cycle = fields.Char(string='Código', required=True)
    time = fields.Integer('Tiempo entre ciclos(Horas)')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
                                   ondelete='cascade')
    duration = fields.Integer('Duración(Horas)')
    volume = fields.Html('Volumen de Trabajo')
