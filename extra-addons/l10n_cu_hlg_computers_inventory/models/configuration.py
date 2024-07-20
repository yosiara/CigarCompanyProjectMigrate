# -*- coding: utf-8 -*-

from odoo import models, fields, api


class NetworkInventoryConfiguration(models.Model):
    _name = 'computers_inventory.configuration'
    _description = 'computers_inventory.configuration'

    send_notification = fields.Boolean(string='Send notification?')
    email = fields.Char(string='Email to send notifications')
    message = fields.Text()

    # Define the components to send notifications...
    motherboard = fields.Boolean(default=True)
    memory = fields.Boolean(default=True)
    storage = fields.Boolean(default=True)
    monitor = fields.Boolean(default=True)
    microprocessor = fields.Boolean(default=True)
    video_card = fields.Boolean(default=True)
    sound_card = fields.Boolean(default=True)
    network = fields.Boolean(default=True)
    input_device = fields.Boolean(default=True)
    modem = fields.Boolean(default=True)
    printer = fields.Boolean(default=False)

    import_motherboard = fields.Boolean("Import Motherboard", default=True)
    import_memory = fields.Boolean("Import Memory", default=True)
    import_storage = fields.Boolean("Import Storage", default=True)
    import_monitor = fields.Boolean("Import Monitor", default=True)
    import_microprocessor = fields.Boolean("Import Microprocessor", default=True)
    import_video_card = fields.Boolean("Import Video Card", default=True)
    import_sound_card = fields.Boolean("Import Sound Card", default=True)
    import_network = fields.Boolean("Import Network", default=True)
    import_input_device = fields.Boolean("Import Input Device", default=True)
    import_modem = fields.Boolean("Import Modem", default=True)
    import_printer = fields.Boolean("Import Printer", default=False)

    #@api.one
    def action_save(self):
        return True


class DBExternalConnector(models.Model):
    _inherit = "db_external_connector.template"
    application = fields.Selection(selection_add=[('ocs_inventory', 'OCS Inventory')])
