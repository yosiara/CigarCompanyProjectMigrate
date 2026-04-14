# -*- coding: utf-8 -*-
from lxml import etree

from odoo.exceptions import ValidationError
from odoo.http import addons_manifest
from odoo import models
from odoo.tools.translate import _

resp_dic = {'nokey': _('You must request a registry key. Please contact the support center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the support center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the support center for a new one.'),
            'invalidmod': _('You are using a invalid key. Please contact the support center for a new one.')}


class UpdateDpaData(models.TransientModel):
    _name = 'l10n_cu_hlg_uforce.update_dpa_wzd'

    def update_dpa_data(self):
        # check_reg
        #resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_hlg_uforce')
        #if resp != 'ok':
            #raise ValidationError(resp_dic[resp])

        data = '/l10n_cu_hlg_uforce/data/res_country_state_data.xml'
        path = addons_manifest['l10n_cu_hlg_uforce']['addons_path'] + data

        doc = etree.parse(path)
        for record in doc.getroot().findall('record'):
            state = self.env.ref(record.attrib['id'])
            values = {'external_id': 0}
            for field in record.findall('field'):
                values[field.attrib['name']] = field.text
            state.write(values)
            #print('State/Municipality updated -> ' + state.name + ' with external_id -> ' + state.external_id)

        return True
