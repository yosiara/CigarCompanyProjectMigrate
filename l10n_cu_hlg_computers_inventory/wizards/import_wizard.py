# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.exceptions import ValidationError

resp_dic={'nokey':_('You must request a registry key. Please contact the suport center for a new one.'),
          'invalidkey':_('You are using a invalid key. Please contact the suport center for a new one.'),
          'expkey':_('You are using a expired key. Please contact the suport center for a new one.')}

_logger = logging.getLogger(__name__)


class ImportComputersAndComponentsWizard(models.TransientModel):
    _name = "computers_inventory.import_computers_wizard"

    def _get_default_connector(self):
        return self.env['db_external_connector.template'].search(
            [('application', '=', 'ocs_inventory')], limit=1
        ).id or False

    connector_id = fields.Many2one(
        'db_external_connector.template',  'Database',  required=True, default=_get_default_connector
    )

    import_software = fields.Boolean('Import Software', default=False)

    #@api.multi
    def action_import(self):
        self.action_import_function()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('l10n_cu_hlg_computers_inventory.menu_computers_inventory_root').id},
        }

    @api.model
    def action_import_function(self):
        obj = self
        connector_obj = self.env['db_external_connector.template']
        args = [('application', '=', 'ocs_inventory')]

        if not self.connector_id:
            obj = self.create({'connector_id': connector_obj.search(args, limit=1).id})

        connection = obj.connector_id.connect()
        obj.import_equipments_from_ocs_database(connection)
        connection.close()

        # Sending notification...
        conf = self.env['computers_inventory.configuration'].search([], limit=1)
        if conf.send_notification and conf.email:
            self._send_mail({
                'auto_delete': True,
                'state': 'outgoing',
                'email_from': self.env.user.company_id.email,
                'email_to': conf.email,
                'subject': _('Computers inventory system.'),
                'body_html': _('Computers inventory executed according to schedule...')
            })

        return True

    #@api.one
    def import_equipments_from_ocs_database(self, connection):
        cursor = connection.cursor()
        query = """SELECT TAG, ID, UUID, NAME, OSNAME, OSVERSION, LASTDATE, USERID, UUID, ARCH, IPADDR, WORKGROUP
                   FROM hardware
                   INNER JOIN accountinfo ON accountinfo.HARDWARE_ID = hardware.ID;"""

        records = self._execute_query(cursor, query)
        # Updating equipments list from ocs-inventory database...
        equipment_obj = self.env['maintenance.equipment']

        for record in records:
            equipment_data_values = {
                'inventory_number': tools.ustr(record[0]),
                'ocs_external_id': tools.ustr(record[1]),
                'serial_no': tools.ustr(record[2]),
                'name': tools.ustr(record[3]),
                'operative_system': tools.ustr(record[4]),
                'os_version': tools.ustr(record[5]),
                'information_updated_date': tools.ustr(record[6]),
                'user_name': tools.ustr(record[7]),
                'uuid': tools.ustr(record[8]),
                'architecture': tools.ustr(record[9]),
                'ip_address': tools.ustr(record[10]),
                'domain': tools.ustr(record[11]),
                'is_a_computer': True,
            }

            equipments = equipment_obj.search(
                ['|', ('serial_no', '=', tools.ustr(record[2])), ('ocs_external_id', '=', tools.ustr(record[1]))], limit=1
            )

            if not len(equipments):
                equipment_obj.create(equipment_data_values)
                _logger.info("Imported equipment: %s-%s" % (tools.ustr(record[1]), tools.ustr(record[3])))
            else:
                equipments.write(equipment_data_values)

        conf = self.env['computers_inventory.configuration'].search([], limit=1)

        # Updating components and software information for each computer in ocs-inventory database...
        equipments = equipment_obj.search([('is_a_computer', '=', True), ('ocs_external_id', '!=', False)])
        if self.import_software:
            self.env['equipment.software'].search([('equipment_id', 'in', equipments.ids), ('ocs_external_id', '!=', False), ('ocs_external_id', '!=', 0)]).unlink()
        for equipment in equipments:
            self._update_equipment_components(connection, equipment)
            _logger.info("Updated equipment's components: %s" % (equipment.name,))
            send_notification = False

            if equipment.importation_state == '3':
                if equipment.quantity_movements_for_approval and conf.send_notification and conf.email:
                    for movement in equipment.movement_for_approval_ids:
                        if getattr(conf, movement.component_id.component_type, False):
                            send_notification = True
                            break

                    if send_notification:
                        args = [('equipment_id', '=', equipment.id), ('state', '=', 'waiting_approval')]
                        if len(self.env['equipment.component_movement'].search(args)):
                            body = _("""Alerta de movimiento de componentes... <br/><br/>
                                        El equipo: %s ha sufrido cambios en sus componentes.""")

                            self._send_mail({
                                'auto_delete': True,
                                'state': 'outgoing',
                                'email_from': self.env.user.company_id.email,
                                'email_to': conf.email,
                                'subject': _('Alert...'),
                                'body_html': body % (equipment.name,)
                            })

            if equipment.importation_state != '3':
                equipment.approve_all_movements()
                equipment.importation_state = '3'
            self._cr.commit()

        return True

    def _update_equipment_components(self, connection, equipment):
        conf = self.env['computers_inventory.configuration'].search([], limit=1)
        if conf.import_monitor:
            self._update_monitor_information(connection, equipment)
        if conf.import_motherboard:
            self._update_bios_information(connection, equipment)
        if conf.import_microprocessor:
            self._update_microprocessor_information(connection, equipment)
        if conf.import_memory:
            self._update_ram_slot_information(connection, equipment)
        if conf.import_storage:
            self._update_storage_media_information(connection, equipment)
        if conf.import_video_card:
            self._update_video_card_information(connection, equipment)
        if conf.import_sound_card:
            self._update_sound_card_information(connection, equipment)
        if conf.import_network:
            self._update_network_information(connection, equipment)
        if conf.import_input_device:
            self._update_input_device_information(connection, equipment)
        if conf.import_printer:
            self._update_printers_information(connection, equipment)
        if conf.import_modem:
            self._update_modem_information(connection, equipment)
        if self.import_software:
            self._update_software_information(connection, equipment)

    def _send_mail(self, vals):
        try:
            mail_obj = self.env['mail.mail']
            mail = mail_obj.create(vals)
            mail.send()

        finally:
            return True

    def _update_monitor_information(self, connection, equipment):
        query = """SELECT monitors.ID, monitors.MANUFACTURER, monitors.CAPTION, monitors.DESCRIPTION,
                          monitors.TYPE, monitors.SERIAL
                   FROM monitors
                   INNER JOIN hardware ON monitors.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'name': tools.ustr('Monitor / ' + tools.ustr(record[2])),
                'manufactured_date': tools.ustr(record[3]),
                'equipment_id': equipment.id,
                'component_type': 'monitor',
                'manufacturer': tools.ustr(record[1]),
                'serial_no': tools.ustr(record[5]),
                'model': tools.ustr(record[2]),
                'type': tools.ustr(record[4]),
                'is_active': True,
            }

            args = [('component_type', '=', 'monitor'), ('equipment_id', '=', equipment.id), ('serial_no', '=', tools.ustr(record[5]))]
            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'monitor'), 'monitors', 'SERIAL')
        cursor.close()
        return True

    def _update_bios_information(self, connection, equipment):
        query = """SELECT bios.MMANUFACTURER, bios.MMODEL, bios.TYPE, bios.BVERSION, hardware.UUID,
                          bios.MSN, hardware.ID, bios.HARDWARE_ID, bios.SMODEL
                   FROM bios
                   INNER JOIN hardware ON bios.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[7]),
                'name': tools.ustr(record[0] + ' ' + record[1]),
                'component_type': 'motherboard',
                'equipment_id': equipment.id,
                'manufacturer': tools.ustr(record[0]),
                'serial_no': tools.ustr(record[5]),
                'version': tools.ustr(record[3]),
                'model': tools.ustr(record[1]) if tools.ustr(record[1]) else tools.ustr(record[8]),
                'type': tools.ustr(record[2]),
                'is_active': True,
            }

            args = [('component_type', '=', 'motherboard'), ('equipment_id', '=', equipment.id), ('ocs_external_id', '=', tools.ustr(record[7]))]
            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'motherboard'), 'bios')
        cursor.close()
        return True

    def _update_microprocessor_information(self, connection, equipment):
        query = """SELECT cpus.ID, cpus.MANUFACTURER, cpus.TYPE, cpus.SERIALNUMBER, cpus.CORES,
                          cpus.CPUARCH, cpus.SPEED, cpus.SOCKET
                   FROM cpus
                   INNER JOIN hardware ON cpus.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'name': tools.ustr(record[2]),
                'manufacturer': tools.ustr(record[1]),
                'equipment_id': equipment.id,
                'component_type': 'microprocessor',
                'cores_number': tools.ustr(record[4]),
                'architecture': tools.ustr(record[5]),
                'socket_type': tools.ustr(record[7]),
                'frequency': tools.ustr(record[6]),
                'serial_no': tools.ustr(record[3]),
                'type': tools.ustr(record[2]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'microprocessor'), ('equipment_id', '=', equipment.id),('ocs_external_id', '=', tools.ustr(record[0])), ('type', '=', tools.ustr(record[2])), ('architecture', '=', tools.ustr(record[5])),
                ('socket_type', '=', tools.ustr(record[7]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'microprocessor'), 'cpus', 'ID')
        cursor.close()
        return True

    def _update_ram_slot_information(self, connection, equipment):
        query = """SELECT memories.ID, memories.CAPTION, memories.DESCRIPTION, memories.CAPACITY,
                          memories.TYPE, memories.NUMSLOTS, memories.SERIALNUMBER, memories.SPEED
                   FROM memories
                   INNER JOIN hardware ON memories.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d and memories.TYPE != 'Empty slot';""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'serial_no': tools.ustr(record[6]),
                'name': tools.ustr(record[1]),
                'equipment_id': equipment.id,
                'component_type': 'memory',
                'type': tools.ustr(record[4]),
                'speed': tools.ustr(record[7]),
                'capacity': tools.ustr(record[3]),
                'slot_used': tools.ustr(record[5]),
                'slot_description': tools.ustr(record[2]),
                'is_active': True,
            }

            args = [('component_type', '=', 'memory'), ('equipment_id', '=', equipment.id), ('serial_no', '=', tools.ustr(record[6])), ('slot_used', '=', tools.ustr(record[5])), ('capacity', '=', tools.ustr(record[3]))]
            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'memory'), 'memories', 'SERIALNUMBER')
        cursor.close()
        return True

    def _update_storage_media_information(self, connection, equipment):
        query = """SELECT storages.ID, storages.MANUFACTURER, storages.NAME, storages.MODEL, storages.DESCRIPTION,
                          storages.TYPE, storages.DISKSIZE, storages.SERIALNUMBER, storages.FIRMWARE
                   FROM storages
                   INNER JOIN hardware ON storages.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d and storages.TYPE != 'Removable Media' and storages.TYPE != '' and storages.TYPE is not NULL;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'serial_no': tools.ustr(record[7]),
                'name': tools.ustr(record[2]),
                'equipment_id': equipment.id,
                'component_type': 'storage',
                'type': tools.ustr(record[5]),
                'model': tools.ustr(record[2]),
                'manufacturer': tools.ustr(record[1]),
                'description': tools.ustr(record[4]),
                'disk_size': tools.ustr(record[6]),
                'firmware': tools.ustr(record[8]),
                'is_active': True,
            }

            args = [('component_type', '=', 'storage'), ('equipment_id', '=', equipment.id), ('serial_no', '=', tools.ustr(record[7])), ('model', '=', tools.ustr(record[2]))]
            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'storage'), 'storages', 'SERIALNUMBER')
        cursor.close()
        return True

    def _update_video_card_information(self, connection, equipment):
        query = """SELECT videos.ID, videos.NAME, videos.CHIPSET, videos.MEMORY, videos.RESOLUTION
                   FROM videos
                   INNER JOIN hardware ON videos.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d and videos.MEMORY;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'name': tools.ustr(record[1]),
                'equipment_id': equipment.id,
                'component_type': 'video_card',
                'memory': tools.ustr(record[3]),
                'chipset': tools.ustr(record[2]),
                'resolution': tools.ustr(record[4]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'video_card'), ('equipment_id', '=', equipment.id), ('name', '=', tools.ustr(record[1])), ('chipset', '=', tools.ustr(record[2])),
                ('memory', '=', tools.ustr(record[3]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'video_card'), 'videos', 'ID')
        cursor.close()
        return True

    def _update_sound_card_information(self, connection, equipment):
        query = """SELECT sounds.ID, sounds.MANUFACTURER, sounds.NAME, sounds.DESCRIPTION
                   FROM sounds
                   INNER JOIN hardware ON sounds.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'name': tools.ustr(record[2]),
                'equipment_id': equipment.id,
                'component_type': 'sound_card',
                'description': tools.ustr(record[3]),
                'manufacturer': tools.ustr(record[1]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'sound_card'), ('equipment_id', '=', equipment.id), ('name', '=', tools.ustr(record[2])),
                ('manufacturer', '=', tools.ustr(record[1]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'sound_card'), 'sounds', 'ID')
        cursor.close()
        return True

    def _update_network_information(self, connection, equipment):
        query = """SELECT networks.ID, networks.DESCRIPTION, networks.TYPE, networks.SPEED, networks.MACADDR,
                          networks.STATUS, networks.IPADDRESS
                   FROM networks
                   INNER JOIN hardware ON networks.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d and networks.DESCRIPTION NOT LIKE '%%Virtual%%' and networks.MACADDR != '00:00:00:00:00:00';""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'equipment_id': equipment.id,
                'component_type': 'network',
                'name': tools.ustr(record[1]),
                'type': tools.ustr(record[2]),
                'speed': tools.ustr(record[3]),
                'mac': tools.ustr(record[4]),
                'serial_no': tools.ustr(record[4]),
                'status': tools.ustr(record[5]),
                'ip': tools.ustr(record[6]),
                'is_active': True,
            }

            args = [('component_type', '=', 'network'), ('equipment_id', '=', equipment.id), ('serial_no', '=', tools.ustr(record[4])), ('name', '=', tools.ustr(record[1]))]
            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'network'), 'networks', 'MACADDR')
        cursor.close()
        return True

    def _update_input_device_information(self, connection, equipment):
        query = """SELECT inputs.ID, inputs.DESCRIPTION, inputs.TYPE, inputs.MANUFACTURER, inputs.CAPTION,
                          inputs.INTERFACE
                   FROM inputs
                   INNER JOIN hardware ON inputs.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'equipment_id': equipment.id,
                'component_type': 'input_device',
                'name': tools.ustr(record[1]),
                'type': tools.ustr(record[2]),
                'description': tools.ustr(record[4]),
                'manufacturer': tools.ustr(record[3]),
                'interface': tools.ustr(record[5]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'input_device'), ('equipment_id', '=', equipment.id), ('name', '=', tools.ustr(record[1])), ('type', '=', tools.ustr(record[2])),
                ('description', '=', tools.ustr(record[4])), ('interface', '=', tools.ustr(record[5]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'input_device'), 'inputs', 'ID')
        cursor.close()
        return True

    def _update_printers_information(self, connection, equipment):
        query = """SELECT printers.ID, printers.NAME, printers.DESCRIPTION, printers.DRIVER, printers.PORT
                   FROM printers
                   INNER JOIN hardware ON printers.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d and printers.PORT NOT LIKE '%%PORTPROMPT%%' and printers.PORT NOT LIKE '%%PDF%%' and printers.PORT NOT LIKE '%%SHRFAX%%' and printers.PORT NOT LIKE '%%FOXIT%%' and printers.PORT NOT LIKE '%%OneNote%%';""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'equipment_id': equipment.id,
                'component_type': 'printer',
                'name': tools.ustr(record[1]),
                'description': tools.ustr(record[2]),
                'driver': tools.ustr(record[3]),
                'port': tools.ustr(record[4]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'printer'), ('equipment_id', '=', equipment.id), ('name', '=', tools.ustr(record[1])), ('driver', '=', tools.ustr(record[3])),
                ('port', '=', tools.ustr(record[4]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'printer'), 'printers', 'ID')
        cursor.close()
        return True

    def _update_modem_information(self, connection, equipment):
        query = """SELECT modems.ID, modems.DESCRIPTION, modems.TYPE, modems.MODEL, modems.NAME
                   FROM modems
                   INNER JOIN hardware ON modems.HARDWARE_ID = hardware.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)
        new_or_updated_records = []

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'equipment_id': equipment.id,
                'component_type': 'modem',
                'name': tools.ustr(record[4]),
                'type': tools.ustr(record[2]),
                'description': tools.ustr(record[1]),
                'model': tools.ustr(record[3]),
                'is_active': True,
            }

            args = [
                ('component_type', '=', 'modem'), ('equipment_id', '=', equipment.id), ('name', '=', tools.ustr(record[4])), ('model', '=', tools.ustr(record[3])),
                ('description', '=', tools.ustr(record[1])), ('type', '=', tools.ustr(record[2]))
            ]

            new_or_updated_records.extend(self._search_create_or_update(
                self.env['equipment.component'], equipment, values, args
            ))

        self._create_up_movements(new_or_updated_records)
        self._check_components(cursor, equipment.component_ids.filtered(lambda comp: comp.component_type == 'modem'), 'modems', 'ID')
        cursor.close()
        return True

    @api.model
    def _update_software_information(self, connection, equipment):
        query = """SELECT software.ID, software_name.NAME, software_publisher.PUBLISHER, software_version.VERSION, software.COMMENTS
                   FROM software
                   INNER JOIN hardware ON software.HARDWARE_ID = hardware.ID
                   INNER JOIN software_name ON software.NAME_ID = software_name.ID
                   INNER JOIN software_version ON software.VERSION_ID = software_version.ID
                   INNER JOIN software_publisher ON software.PUBLISHER_ID = software_publisher.ID
                   WHERE hardware.ID = %d;""" % (equipment.ocs_external_id,)

        cursor = connection.cursor()
        records = self._execute_query(cursor, query)

        for record in records:
            values = {
                'ocs_external_id': tools.ustr(record[0]),
                'equipment_id': equipment.id,
                'name': tools.ustr(record[1]),
                'publisher': tools.ustr(record[2]),
                'version': tools.ustr(record[3]),
                'notes': tools.ustr(record[4]),
            }

            self.env['equipment.software'].create(values)

        cursor.close()
        return True

    def _execute_query(self, cursor, query):
        try:
            cursor.execute(query)
        except Exception, e:
            cursor.close()
            _logger.info(e)
            raise UserError(
                _("""The operation has not been completed. Please, check the connection of the Database
                     and make sure to select the correct one...""")
            )

        return cursor.fetchall()

    def _search_create_or_update(self, obj, equipment, values, args):
        components = obj.search(args, limit=1)
        new_or_updated_records = []

        if not len(components):
            new_or_updated_records.append(obj.create(values))
        else:
            if not components[0].is_active:
                new_or_updated_records.append(components[0])
                components[0].is_active = True
            components.write(values)

        return new_or_updated_records

    def _check_components(self, cursor, components, table='', serial_column_name='ID'):
        for component in components:
            if component.ocs_external_id:
                if table != '':
                    query = """SELECT *
                               FROM %s
                               INNER JOIN hardware ON %s.HARDWARE_ID = hardware.ID
                               WHERE hardware.ID = %d
                               AND %s.ID = %s;""" % (table, table, component.equipment_id.ocs_external_id, table,
                                                     component.ocs_external_id)

                    if serial_column_name != 'ID':
                        query = """SELECT * FROM %s
                                   INNER JOIN hardware ON %s.HARDWARE_ID = hardware.ID
                                   WHERE hardware.ID = %d
                                   AND %s.%s = '%s';""" % (table, table, component.equipment_id.ocs_external_id, table,
                                                           serial_column_name, component.serial_no)

                    if table == 'bios':
                        query = """SELECT *
                                   FROM hardware
                                   WHERE hardware.ID = '%s';""" % (component.ocs_external_id,)

                    records = self._execute_query(cursor, query)
                    if not len(records):
                        component.is_active = False
                        self._create_down_movements([component])

    def _create_up_movements(self, components):
        for component in components:
            component.equipment_id.quantity_movements_for_approval = component.equipment_id.quantity_movements_for_approval + 1
            self.env['equipment.component_movement'].create({
                'datetime': fields.Datetime.now(),
                'equipment_id': component.equipment_id.id,
                'component_id': component.id,
                'type': 'up'
            })

    def _create_down_movements(self, components):
        for component in components:
            component.equipment_id.quantity_movements_for_approval = component.equipment_id.quantity_movements_for_approval + 1
            self.env['equipment.component_movement'].create({
                'datetime': fields.Datetime.now(),
                'equipment_id': component.equipment_id.id,
                'component_id': component.id,
                'type': 'down'
            })

    #@api.one
    @api.constrains('connector_id')
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_computers_inventory')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])
