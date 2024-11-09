# -*- coding: utf-8 -*-


from datetime import datetime
from odoo import models, fields, api

class ProductiveSectionPlan(models.Model):
    _name = 'turei_process_control.productive_section_plan'

    indice_planif_efici_real = fields.Float(string="Ind Eficiencia (%)", required=True, default=0.00)
    indice_planif_rechazo = fields.Float(string="Ind Rechazo (%)", required=True, default=0.00)
    indice_planif_disp_tec = fields.Float(string="Ind disp.Técnica (%)", required=True, default=0.00)
    indice_planif_norma = fields.Float(string="Norma plan", required=True, default=0.00)

    def _default_year(self):
        date = str(fields.Datetime.now())
        return datetime.strptime(date.split('-')[0], '%Y').year

    year = fields.Char(string="Año", required=True, default=_default_year)
    active = fields.Boolean(string="Activo", default=True)

    productive_section_ids = fields.Many2many(comodel_name="turei_process_control.productive_section", relation="turei_process_control_productive_section_plan_relation", column1="plan_id",
                                             column2="productive_section_plan_id", string="Secciones productivas",
                                             required=False, )
    name = fields.Char(string='Nombre', required=True)
    productive_capacity = fields.Integer('Capacidad Productiva', required=True)
    quantity_line = fields.Integer('Cantidad Líneas Trabajando', required=True)

    @api.multi
    @api.depends('year')
    def get_name(self):
        for plan in self:
            if plan.id and plan.year:
                plan.name = plan.year+' # '+str(plan.id)
            else:
                plan.name = ' # '

    @api.model
    def create(self, vals):
        plan_id = super(ProductiveSectionPlan, self).create(vals)
        if plan_id.active:
            self.search([('id', '!=', plan_id.id), ('year', '!=', plan_id.year)]).write({'active': False})
        return plan_id

    @api.multi
    def write(self, vals):
        if vals.get('active'):
            self.search([]).write({'active': False})
        return super(ProductiveSectionPlan, self).write(vals)
