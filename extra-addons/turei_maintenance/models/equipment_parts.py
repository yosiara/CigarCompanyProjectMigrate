# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class EquipmentParts(models.Model):
    _name = 'turei_maintenance.equipment_parts'

    name = fields.Char(required=True, string='Nombre')
    item = fields.Char(string='Item')
    code = fields.Char(string='Código')
    note = fields.Text(string="Descripción del Proveedor")
    fabricator = fields.Char(string='Fabricante')
    # quantity = fields.Float(digits=(16, 2), required=True, string='Cantidad')
    reference = fields.Char(string='Referencia o Localización')
    # equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
    #                                  ondelete='cascade')
    # equipment_ids = fields.One2many(comodel_name='turei_maintenance.equipment_parts_item', inverse_name='equipment_parts_id',
    #                                       string='Equipos')
    equipment_ids = fields.Many2many('maintenance.equipment', 'equipment_parts_rel', 'equipment_id',
                                       'equipment_parts_id', 'Equipos')


class EquipmentPartsItem(models.Model):
    _name = 'turei_maintenance.equipment_parts_item'

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos")
    equipment_parts_id = fields.Many2one(comodel_name="turei_maintenance.equipment_parts", string="Piezas")

