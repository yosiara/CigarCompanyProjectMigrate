import base64
import os
import tempfile
from datetime import datetime

import xlrd
from odoo import models, api, fields, tools
from odoo.exceptions import ValidationError, _logger
from odoo.tools.translate import _



class ImportRetiredExcel(models.TransientModel):
    _name = "turei_retired_person.import_retired_wizard"

    file_data = fields.Binary('Select template', required=True)
    file_name = fields.Char('File Name')



    @api.multi
    def action_import_retired(self):

        file_path = tempfile.gettempdir() + '/file.xlsx'
        data = self.file_data
        f = open(file_path, 'wb')
        f.write(base64.decodestring(data))
        f.close()

        dir_excel = str(self.file_name).split('.')
        file_format = dir_excel[len(dir_excel) - 1]
        if file_format not in ('xls', 'xlsx'):
            raise ValidationError(_('Please, select the correct file!'))

        wb = xlrd.open_workbook(file_path)
        xl_sheet = wb.sheet_by_index(0)
        gender = 'Female'

        retired_person_obj = self.env['turei_retired_person.retired_person']
        hire_drop_obj = self.env['l10n_cu_hlg_uforce.hire_drop_record']

        for row_idx in range(2, xl_sheet.nrows):
            retired_name = tools.ustr(xl_sheet.cell(row_idx, 0).value)
            ci = int(xl_sheet.cell(row_idx, 1).value)

            if len(tools.ustr(xl_sheet.cell(row_idx, 1).value)) == 11:
                if int(self.identification_id[9]) % 2 == 0:
                    gender = 'Male'


            if tools.ustr(xl_sheet.cell(row_idx, 2).value) == '' and xl_sheet.cell(row_idx, 1).value == '':
                raise Warning(_("Please give an CI or born date!"))

            if tools.ustr(xl_sheet.cell(row_idx, 2).value) == '':
                borndate = False
            else:
                borndate = datetime.strptime(tools.ustr(xl_sheet.cell(row_idx, 2).value), '%d-%m-%Y')

            if tools.ustr(xl_sheet.cell(row_idx, 3).value) != '' and xl_sheet.cell(row_idx, 1).value == '':
                gender = tools.ustr(xl_sheet.cell(row_idx, 3).value)

            retired_date = datetime.strptime(tools.ustr(xl_sheet.cell(row_idx, 4).value), '%d-%m-%Y')

            if tools.ustr(xl_sheet.cell(row_idx, 6).value) != '':
                neighborhood_id = self.env['app_seleccion.reparto'].search([('name','=',tools.ustr(xl_sheet.cell(row_idx, 6).value))],limit=1).id

            address = tools.ustr(xl_sheet.cell(row_idx, 5).value)

            if tools.ustr(xl_sheet.cell(row_idx, 7).value) == '':
                raise Warning(_("Please give an Municipality!"))

            municipality_id = self.env['l10n_cu_base.municipality'].search([('name','=',tools.ustr(xl_sheet.cell(row_idx, 7).value))])

            if tools.ustr(xl_sheet.cell(row_idx, 8).value) == '':
                raise Warning(_("Please give an State!"))
            state_id = self.env['res.country.state'].search([('name','=',tools.ustr(xl_sheet.cell(row_idx, 8).value))])


            retired_data = {
                'identification_id': ci,
                'name': retired_name,
                'born_date': borndate,
                'gender': gender,
                'retired_date': retired_date,
                'address': address,
                'neighborhood_id': neighborhood_id,
                'municipality_id': municipality_id.id,
                'state_id': state_id.id
            }

            retired_person = retired_person_obj.search([('identification_id', '=', ci)], limit=1)

            if not retired_person.id:
                retired = retired_person_obj.create(retired_data)
                _logger.info("Retired person created: %s." % retired.name)
            else:
                retired_person.write(retired_data)
                _logger.info("Employee updated: %s." % retired_person.name)



        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('turei_retired_person.menu_retired_person_item').id},
        }




