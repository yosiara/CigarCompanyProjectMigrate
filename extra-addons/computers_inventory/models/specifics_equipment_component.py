# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EquipmentComponentMotherBoard(models.Model):
    _name = 'equipment.component.motherboard'
    _description = 'equipment.component.motherboard'
    _inherits = {'equipment.component': 'component_id'}

    version = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentMonitor(models.Model):
    _name = 'equipment.component.monitor'
    _description = 'equipment.component.monitor'
    _inherits = {'equipment.component': 'component_id'}

    manufactured_date = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentMicroProcessor(models.Model):
    _name = 'equipment.component.microprocessor'
    _description = 'equipment.component.microprocessor'
    _inherits = {'equipment.component': 'component_id'}

    frequency = fields.Char()
    socket_type = fields.Char()
    architecture = fields.Char()
    cores_number = fields.Integer()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentRam(models.Model):
    _name = 'equipment.component.ram_slot'
    _description = 'equipment.component.ram_slot'
    _inherits = {'equipment.component': 'component_id'}

    speed = fields.Char()
    capacity = fields.Char()
    slot_used = fields.Integer()
    slot_description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentStorageMedia(models.Model):
    _name = 'equipment.component.storage_media'
    _description = 'equipment.component.storage_media'
    _inherits = {'equipment.component': 'component_id'}

    firmware = fields.Char()
    description = fields.Char()
    disk_size = fields.Integer()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentVideoCard(models.Model):
    _name = 'equipment.component.video_card'
    _description = 'equipment.component.video_card'
    _inherits = {'equipment.component': 'component_id'}

    memory = fields.Char()
    chipset = fields.Char()
    resolution = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentSoundCard(models.Model):
    _name = 'equipment.component.sound_card'
    _description = 'equipment.component.sound_card'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentNetwork(models.Model):
    _name = 'equipment.component.network'
    _description = 'equipment.component.network'
    _inherits = {'equipment.component': 'component_id'}

    ip = fields.Char()
    mac = fields.Char()
    status = fields.Char()
    speed = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentInputDevice(models.Model):
    _name = 'equipment.component.input_device'
    _description = 'equipment.component.input_device'
    _inherits = {'equipment.component': 'component_id'}

    interface = fields.Char()
    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentModem(models.Model):
    _name = 'equipment.component.modem'
    _description = 'equipment.component.modem'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentPrinter(models.Model):
    _name = 'equipment.component.printer'
    _description = 'equipment.component.printer'
    _inherits = {'equipment.component': 'component_id'}

    port = fields.Char()
    driver = fields.Char()
    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentUPS(models.Model):
    _name = 'equipment.component.ups'
    _description = 'equipment.component.ups'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentFax(models.Model):
    _name = 'equipment.component.fax'
    _description = 'equipment.component.fax'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentScanner(models.Model):
    _name = 'equipment.component.scanner'
    _description = 'equipment.component.scanner'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentOpticalDrive(models.Model):
    _name = 'equipment.component.optical_drive'
    _description = 'equipment.component.optical_drive'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )


class EquipmentComponentOpticalSpeaker(models.Model):
    _name = 'equipment.component.speaker'
    _description = 'equipment.component.speaker'
    _inherits = {'equipment.component': 'component_id'}

    description = fields.Char()
    component_id = fields.Many2one(
        'equipment.component', string='Component', auto_join=True, index=True, ondelete='cascade', required=True
    )
