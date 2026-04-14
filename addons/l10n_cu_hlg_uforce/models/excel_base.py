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

from xlwt import *
from odoo.tools import float_round


class ExcelBase(object):
    def __init__(self, model, cr, uid, context=None):
        self.workbook = Workbook(encoding='utf-8')
        self.model = model
        self.cr = cr
        self.uid = uid
        self.localcontext = context  
    
    def get_data(self, cr, uid, context=None):
        raise NotImplemented()

    def pixel2with(self, pixel):
        return int(round((pixel - 0.446)/0.0272, 0))
    
    def width2pixels(self, width):
        return int(round(width * 0.0272 + 0.446, 0))

    def font_size(self, size):
        return size * 20

    def convert_uom(self, quantity, uom, precision_digits = 3):
        if uom.lower() == 'g':
            return float_round(quantity / 1000, precision_digits = precision_digits), "kg"
        if uom.lower() == 'ml':
            return float_round(quantity / 1000, precision_digits = precision_digits), "L"
        return float_round(quantity, precision_digits = precision_digits), uom
   
    def print_blank(self, ws, r1, r2, c1, c2, left=1, right=1, top=1, bottom=1, font_size=8):
        """ Print Blank Row"""
        borders1 = Borders()
        borders1.left = left
        borders1.right = right
        borders1.top = top
        borders1.bottom = bottom
        fnt1 = Font()
        fnt1.height = self.font_size(font_size)
        style1 = XFStyle()
        style1.borders = borders1
        style1.font = fnt1
        ws.write_merge(r1, r2, c1, c2, '', style1)
