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




class XlsReportComparaciones(models.TransientModel):
    _name = 'app_seleccion.xls_report_comparaciones'

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

    #validar que se introduzca el año
    @api.constrains('year')
    def _check_year(self):
        if not self.year :
            raise ValidationError(_("Debe introducir el año!!"))

    @api.multi
    def print_report(self):



        datas = {
             'year': self.year,

        }

        return self.env['report'].get_action(self, 'app_seleccion.xls_report_comparaciones', data=datas)

