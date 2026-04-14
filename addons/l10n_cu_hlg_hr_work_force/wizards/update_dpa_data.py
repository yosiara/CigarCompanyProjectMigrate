# -*- coding: utf-8 -*-
from lxml import etree
from odoo.http import addons_manifest
from odoo import models


class UpdateDpaData(models.TransientModel):
    _name = 'l10n_cu_hlg_hr_work_force.update_dpa_wzd'

    def update_dpa_data(self):
        data = '/l10n_cu_hlg_hr_work_force/data/res_country_state_data.xml'
        path = addons_manifest['l10n_cu_hlg_hr_work_force']['addons_path'] + data

        doc = etree.parse(path)
        for record in doc.getroot().findall('record'):
            state = self.env.ref(record.attrib['id'])
            values = {'external_id': 0}
            for field in record.findall('field'):
                values[field.attrib['name']] = field.text
            state.write(values)
            #print('State/Municipality updated -> ' + state.name + ' with external_id -> ' + state.external_id)

        return True
