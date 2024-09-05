# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from odoo.tools.translate import _
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
import base64


class EquipmentComponent(models.Model):
    _name = 'equipment.component'
    _description = 'equipment.component'
    _order = 'component_type'

    serial_no = fields.Char('Serial No OCS', index=True)
    serial_no_custom = fields.Char('Custom Serial No')
    name = fields.Char('Name', required=True, index=True)
    equipment_id = fields.Many2one('maintenance.equipment', 'Equipment', ondelete='cascade', index=True)
    is_active = fields.Boolean(default=True)
    ocs_external_id = fields.Char(index=True)

    type = fields.Char(index=True)
    model = fields.Char()
    model_custom = fields.Char("Custom model")
    manufacturer = fields.Char()
    manufacturer_custom = fields.Char("Custom Manufacturer")
    component_type = fields.Selection(
        [('motherboard', 'MotherBoard'), ('memory', 'Memory'), ('storage', 'Storage'), ('monitor', 'Monitor'),
         ('microprocessor', 'Microprocessor'), ('video_card', 'Video Card'), ('sound_card', 'Sound Card'),
         ('network', 'Network'), ('input_device', 'Input Device'), ('modem', 'Modem'),
         ('printer', 'Printer'), ('ups', 'UPS'), ('fax', 'Fax'), ('scanner', 'Scanner'), ('speaker', 'Speaker'), ('power_source', 'Power Source')], string='Component Type', default='motherboard'
    )

    inventory_number = fields.Char('Inventory Number')
    description = fields.Text()

    # specific motherboard
    version = fields.Char()
    # specific monitor
    manufactured_date = fields.Char()
    # specific microprocessor
    frequency = fields.Char()
    socket_type = fields.Char()
    architecture = fields.Char()
    cores_number = fields.Integer()
    # specific ram
    speed = fields.Char()
    capacity = fields.Char()
    slot_used = fields.Integer()
    slot_description = fields.Char()
    # specific storage
    firmware = fields.Char()
    disk_size = fields.Integer()
    # specific video card
    memory = fields.Char()
    chipset = fields.Char()
    resolution = fields.Char()
    # specific network
    ip = fields.Char()
    mac = fields.Char()
    status = fields.Char()
    speed = fields.Char()
    # specific input device
    interface = fields.Char()
    # specific printer
    port = fields.Char()
    driver = fields.Char()

    specific_properties_str = fields.Text('Specific Properties', compute='_compute_specific_properties')

    qrcode_image = fields.Binary("QRCode", compute='get_qrimage')

    @api.onchange('manufacturer_custom', 'model_custom')
    def _onchange_manufacturer_model(self):
        if not self.ocs_external_id and self.manufacturer_custom and self.model_custom:
            return {'value': {'name': '%s / %s' % (self.manufacturer_custom, self.model_custom)}}


    #@api.one
    @api.depends('name', 'equipment_id', 'inventory_number')
    def get_qrimage(self):
        options = {'width': 100 * mm, 'height': 100 * mm}
        name = self.name if self.name else ''

        qr_code = _('Name: %s\n') % name
        qr_code += _('Assign To Equipment: %s\n') % self.equipment_id.inventory_number
        qr_code += _('Local: %s\n') % (self.equipment_id.local_id.name if self.equipment_id.local_id else '')
        qr_code += _('Inventory Number: %s\n') % (self.inventory_number if self.inventory_number else '')
        ret_val = createBarcodeDrawing('QR', value=tools.ustr(qr_code), **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))

    #@api.multi
    def _compute_specific_properties(self):
        for record in self:
            if record.component_type == 'motherboard':
                record.specific_properties_str = _('Version: %s') % record.version
            elif record.component_type == 'memory':
                record.specific_properties_str = _('Speed: %s\nCapacity: %s\nSlot used: %s\nSlot description: %s\n') % (record.speed, ('%.0fGB') % (float(record.capacity) / 1024), record.slot_used, record.slot_description)
            elif record.component_type == 'monitor':
                record.specific_properties_str = _('Manufactured date: %s') % record.manufactured_date
            elif record.component_type == 'microprocessor':
                record.specific_properties_str = _('Frequency: %s\nSocket Type: %s\nArchitecture: %s\nCores Number: %s\n') % (record.frequency, record.socket_type, record.architecture, record.cores_number)
            elif record.component_type == 'storage':
                record.specific_properties_str = _('Firmware: %s\nDisk size: %s') % (record.firmware, ('%.0fGB') % (float(record.disk_size) / 1024))
            elif record.component_type == 'video_card':
                record.specific_properties_str = _('Memory: %s\nChipset: %s\nResolution: %s\n') % (record.memory, record.chipset, record.resolution)
            elif record.component_type == 'network':
                record.specific_properties_str = _('Ip: %s\nMAC: %s\nStatus: %s\nSpeed: %s\n') % (record.ip, record.mac, record.status, record.speed)
            elif record.component_type == 'input_device':
                record.specific_properties_str = _('Interface: %s') % record.interface
            elif record.component_type == 'printer':
                record.specific_properties_str = _('Port: %s\nDriver: %s') % (record.port, record.driver)
            else:
                record.specific_properties_str = record.description
