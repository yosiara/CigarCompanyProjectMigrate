# -*- coding: utf-8 -*-
import base64
import os
import tempfile
from datetime import datetime

import xlrd
from odoo import models, api, fields, tools
from odoo.exceptions import ValidationError, _logger
from odoo.tools.translate import _



class UpdateRetired(models.TransientModel):
    _name = "turei_retired_person.update_retired_wizard"


    @api.multi
    def action_update_retired(self):
        motive_description = 'Jubilación del Trabajador.'
        retired_person_obj = self.env['turei_retired_person.retired_person']
        hire_drop_obj = self.env['l10n_cu_hlg_uforce.hire_drop_record'].search([])
        motive_retired_id = self.env['hr_contract.supplement_motive'].search([('name','=',motive_description)],limit=1).id

        for hr in hire_drop_obj:
            rp = retired_person_obj.search([('name','=',hr.name)])
            if not rp.id and hr.motive_id.id == motive_retired_id:
                retired_data = {
                    'identification_id': False,
                    'name': hr.name,
                    'born_date': False,
                    'gender': False,
                    'retired_date': hr.record_date,
                    'address': False,
                    'neighborhood_id': False,
                    'municipality_id': False,
                    'state_id': False
                }

                retired_person_obj.create(retired_data)



        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('turei_retired_person.menu_retired_person_item').id},
        }




