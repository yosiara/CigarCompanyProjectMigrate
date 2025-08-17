# -*- coding: utf-8 -*-

from odoo import api, models, fields


class Product(models.Model):
    _inherit = "simple_product.product"
    _order = 'group_number'

    group_number = fields.Char(string='Identificador de Grupo')
    group_name = fields.Char(string='Nombre de Grupo')
    consumption_norm_ids = fields.One2many('atm.consumption_norm', inverse_name='product_id', string='Normas de consumo')

    weight = fields.Float(string='Peso en Kg')
    quantity_in_millions = fields.Float(string='Cantidad en MU')

    origin = fields.Selection([('national', 'Nacional'), ('international', 'Importación')], string='Procedencia')
    destiny_id = fields.Many2one('atm.product_destiny', string='Destino')
    conversion_factor = fields.Float(string='Factor de conversión', default=1.0)
    formula_month_plan = fields.Char(string='Fórmula Plan Mensual', help='Se espera la formula: Plan Mensual / dias laborables')

    is_tool_or_util = fields.Boolean(string='Is util or tool?', compute='_compute_is_tool_or_util')
    is_aft = fields.Boolean(string='AFT?', compute='_compute_is_aft')

    @api.model_create_multi
    @api.depends('account_id')
    def _compute_is_tool_or_util(self):
        for rec in self:
            if rec.account_id.code in [187]:
                rec.is_tool_or_util = True

    @api.model_create_multi
    @api.depends('account_id')
    def _compute_is_aft(self):
        for rec in self:
            if rec.account_id.code in [240, 241, 242, 243, 244, 247, 248, 249, 250, 251]:
                rec.is_aft = True

    
    def _compute_product_controls_as_str(self):
        rep = ""
        cont = 1
        for x in self.product_control_ids:
            rep += x.warehouse_id.code + ': ' + str(x.quantity_system)
            if not len(self.product_control_ids) == cont:
                rep += ', '
            cont += 1
        self.product_control_str = rep

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        warehouse_id = self.env.context.get('warehouse_id', False)
        if not warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            return []

        args = args or []
        product_ids = []

        if warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            ctrl_obj = self.env['warehouse.product_control']
            ctrls = ctrl_obj.search([('warehouse_id', '=', warehouse_id), ('quantity_system', '>', 0.0)])
            product_ids = [ctrl.product_id.id for ctrl in ctrls]

        if name:
            args = ['|', ('code', operator, name), ('name', operator, name)] + args

        if warehouse_id and self.env.context.get('only_products_from_warehouse', False):
            args = [('id', 'in', product_ids)] + args
        return self.search(args, limit=limit).name_get()

    def get_consumption_norm(self, uom_id):
        return self.env['atm.consumption_norm'].search(
            [('product_id', '=', self.id), ('uom_id', '=', uom_id)], limit=1
        ).quantity


class ConsumptionNorm(models.Model):
    _name = 'atm.consumption_norm'
    _description = 'atm.consumption_norm'

    product_id = fields.Many2one('simple_product.product', string='Product')
    uom_id = fields.Many2one('product.uom', 'Unit of Measure', required=True)
    quantity = fields.Float(required=True, digits=(16, 4))


class ProductDestiny(models.Model):
    _name = 'atm.product_destiny'
    _description = 'atm.product_destiny'
    _rec_name = 'code'

    code = fields.Char()
    name = fields.Char()
