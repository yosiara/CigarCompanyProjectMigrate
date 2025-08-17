# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools



class EquipmentElectricMotor(models.Model):
    _name = 'turei_maintenance.equipment_electric_motor'
    _rec_name = 'equipment_id'

    review_frequency = fields.Char(string='Frecuencia de Revisión')
    no_motor = fields.Char(string='No. Motor')
    clase = fields.Char(string='Clase')
    service = fields.Char(string='Servicio')
    hp = fields.Char(string='HP')
    kw = fields.Float(string='KW')
    volts = fields.Char(string='Volts')
    cycles = fields.Integer(string='Ciclos')
    amps = fields.Char(string='Amps')
    rpm = fields.Char(string='RPM')
    phase = fields.Integer(string='Fases')
    model = fields.Char(string='Modelo')
    brand = fields.Char(string='Marca')
    fabricator = fields.Char(string='Fabricante')
    serial_no = fields.Char(string='No. Serie')
    pulley_side = fields.Char(string='Lado Polea')
    cap_side = fields.Char(string='Lado Tapa')
    quantity = fields.Integer(string='Cantidad')
    subset = fields.Char(string='Subconjunto')
    equipment_id = fields.Many2one(comodel_name="maintenance.equipment", string="Equipos",
                                     ondelete='cascade')

    equipment_ids = fields.Many2many('maintenance.equipment', 'equipment_electric_motor_rel', 'equipment_id',
                                     'equipment_electric_motor_id', 'Motores Electricos')

