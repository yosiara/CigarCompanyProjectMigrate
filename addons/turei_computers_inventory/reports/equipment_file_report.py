# -*- coding: utf-8 -*-

from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class EquipmentFileReport(models.AbstractModel):
    _name = 'report.turei_computers_inventory.report_equipment_file_view'

    @api.model
    def render_html(self, docids, data=None):
        if len(docids) > 1:
            raise UserError(_('This report is only available to select only one equipment...'))

        equipment = self.env['maintenance.equipment'].search([('id', '=', docids[0])], limit=1)
        if equipment and not equipment.is_a_computer:
            raise UserError(_('This report is only available to equipment of information technology...'))

        mother = self.env['equipment.component'].search(
            [('component_type', '=', 'motherboard'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        ram = self.env['equipment.component'].search(
            [('component_type', '=', 'memory'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        storages = self.env['equipment.component'].search(
            [('component_type', '=', 'storage'), ('type', 'not in', (u'DVD Writer', u'CD Writer', u'DVD Reader', u'CD Reader')), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        monitors = self.env['equipment.component'].search(
            [('component_type', '=', 'monitor'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)])

        mouse = self.env['equipment.component'].search(
            [('component_type', '=', 'input_device'), ('type', '=', 'Pointing'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        keyboard = self.env['equipment.component'].search(
            [('component_type', '=', 'input_device'), ('type', '=', 'Keyboard'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        micros = self.env['equipment.component'].search(
            [('component_type', '=', 'microprocessor'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        videos = self.env['equipment.component'].search(
            [('component_type', '=', 'video_card'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        sounds = self.env['equipment.component'].search(
            [('component_type', '=', 'sound_card'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        networks = self.env['equipment.component'].search(
            [('component_type', '=', 'network'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        modems = self.env['equipment.component'].search(
            [('component_type', '=', 'modem'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        printer = self.env['equipment.component'].search(
            [('component_type', '=', 'printer'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        ups = self.env['equipment.component'].search(
            [('component_type', '=', 'ups'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        fax = self.env['equipment.component'].search(
            [('component_type', '=', 'fax'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        scanner = self.env['equipment.component'].search(
            [('component_type', '=', 'scanner'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        optical_drive = self.env['equipment.component'].search(
            [('component_type', '=', 'storage'), ('type', 'in', (u'DVD Writer', u'CD Writer', u'DVD Reader', u'CD Reader')), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        speaker = self.env['equipment.component'].search(
            [('component_type', '=', 'speaker'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        power_source = self.env['equipment.component'].search(
            [('component_type', '=', 'power_source'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        docargs = {
            'docs': self.env['maintenance.equipment'].search([('id', '=', docids)], limit=1),
            'mother': mother,
            'rams': ram,
            'storages': storages,
            'monitors': monitors,
            'mouse': mouse,
            'keyboard': keyboard,
            'micros': micros,
            'videos': videos,
            'sounds': sounds,
            'networks': networks,
            'modems': modems,
            'printer': printer,
            'ups': ups,
            'fax': fax,
            'scanner': scanner,
            'optical_drive': optical_drive,
            'speaker': speaker,
            'power_source': power_source,
            'date': datetime.today().strftime('%d/%m/%Y')
        }

        return self.env['report'].render('turei_computers_inventory.report_equipment_file_view', docargs)
