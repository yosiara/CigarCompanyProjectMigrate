# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # ----------------------------- ATM Module -----------------------------#
    is_protected = fields.Boolean(string='Is protected?')
    is_for_contingency = fields.Boolean(string='Is for contingency?')
    contingency_quantity = fields.Integer(string='Quantity', help='Quantity that must be kept for contingencies...')
    do_not_use = fields.Boolean(string='Must it not be used?')
    is_exclusive_product = fields.Boolean(string='Exclusive?', help='Checked if the product if for exclusive use of a area...')
    group_number = fields.Char(string='Identificador de Grupo')
    group_name = fields.Char(string='Nombre de Grupo')
    consumption_norm_ids = fields.One2many('atm.consumption_norm', inverse_name='product_id', string='Normas de consumo')
    conversion_factor = fields.Float(string='Factor de conversión', default=1.0)
    formula_month_plan = fields.Char(string='Fórmula Plan Mensual', help='Se espera la formula: Plan Mensual / dias laborables')
    is_tool_or_util = fields.Boolean(string='Is util or tool?',)# compute='_compute_is_tool_or_util')
    is_aft = fields.Boolean(string='AFT?',)# compute='_compute_is_aft')
    #owner_id = fields.Many2one('hr.employee', string='Owner')
    # weight = fields.Float(string='Peso en Kg')
    # ----------------------------- ATM Module -----------------------------#