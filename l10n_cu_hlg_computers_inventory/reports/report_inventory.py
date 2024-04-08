# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class ReportInventory(models.AbstractModel):
    _name = 'report.l10n_cu_hlg_computers_inventory.report_inventory'

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
            [('component_type', '=', 'storage'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
        )

        monitors = self.env['equipment.component'].search(
            [('component_type', '=', 'monitor'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)])

        inputs = self.env['equipment.component'].search(
            [('component_type', '=', 'input_device'), ('equipment_id', '=', docids[0]), ('is_active', '=', True)]
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

        docargs = {
            'docs': self.env['maintenance.equipment'].search([('id', '=', docids)]),
            'mother': mother,
            'rams': ram,
            'storages': storages,
            'monitors': monitors,
            'inputs': inputs,
            'micros': micros,
            'videos': videos,
            'sounds': sounds,
            'networks': networks,
            'modems': modems
        }

        return self.env['report'].render('l10n_cu_hlg_computers_inventory.report_inventory', docargs)
