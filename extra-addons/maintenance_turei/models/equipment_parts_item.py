# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools

class EquipmentPartsItem(models.Model):
    _name = 'maintenance_turei.equipment_parts_item'
    _description = 'Equipment Parts Item'

    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos")
    equipment_parts_id = fields.Many2one(comodel_name="maintenance_turei.equipment_parts", string="Piezas")