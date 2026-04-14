# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError




class XlsReportCmes(models.TransientModel):
    _name = 'app_seleccion.xls_report_cmes'

    @staticmethod
    def get_nombre_mes(mes):
        if mes == '01':
            return 'enero'
        elif mes == '02':
            return 'febrero'
        elif mes == '03':
            return 'marzo'
        elif mes == '04':
            return 'abril'
        elif mes == '05':
            return 'mayo'
        elif mes == '06':
            return 'junio'
        elif mes == '07':
            return 'julio'
        elif mes == '08':
            return 'agosto'
        elif mes == '09':
            return 'septiembre'
        elif mes == '10':
            return 'octubre'
        elif mes == '11':
            return 'noviembre'
        elif mes == '12':
            return 'diciembre'

    def get_mes(self):
        lista = []
        enero = ('01','enero')
        febrero = ('02','febrero')
        marzo = ('03','marzo')
        abril = ('04','abril')
        mayo = ('05','mayo')
        junio = ('06','junio')
        julio = ('07','julio')
        agosto = ('08','agosto')
        septiembre = ('09','septiembre')
        octubre = ('10','octubre')
        noviembre = ('11','noviembre')
        diciembre = ('12','diciembre')

        lista.append(enero)
        lista.append(febrero)
        lista.append(marzo)
        lista.append(abril)
        lista.append(mayo)
        lista.append(junio)
        lista.append(julio)
        lista.append(agosto)
        lista.append(septiembre)
        lista.append(octubre)
        lista.append(noviembre)
        lista.append(diciembre)

        return lista

    mes = fields.Selection(selection='get_mes')

    def get_year(self):
        fecha_hoy = fields.Date.today()
        year = fecha_hoy.split('-')
        year = int(year[0])

        lista = []
        for i in range(2004,year+1):
            year_reg = (i,i)
            lista.append(year_reg)
        return lista

    year = fields.Selection(selection='get_year')

    #validar que se introduzca el mes
    @api.constrains('mes','year')
    def _check_mes(self):
         if not self.year:
            raise ValidationError(_("Debe introducir el año !!"))
         elif not self.mes:
            raise ValidationError(_("Debe introducir el mes !!"))
         else:
            count = self.env['hr.applicant'].search_count([('mes', '=', self.mes),('year', '=', self.year)])
            if count == 0:
                raise ValidationError(_("No existen solicitudes realizadas durante el mes seleccionado !!"))



    @api.multi
    def print_report(self):



        datas = {
             'mes': self.mes,
             'year': self.year,

        }

        return self.env['report'].get_action(self, 'app_seleccion.xls_report_cmes', data=datas)

