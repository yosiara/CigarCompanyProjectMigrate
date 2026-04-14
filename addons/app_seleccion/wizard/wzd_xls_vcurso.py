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




class XlsReportVCurso(models.TransientModel):
    _name = 'app_seleccion.xls_report_vcurso'

    curso_id = fields.Many2one('app_seleccion.curso',track_visibility='onchange')

    @api.constrains('curso_id')
    def _check_curso(self):
         if not self.curso_id:
             raise ValidationError(_("Debe escoger el Curso de Habilitacion !!"))
         else:
             candidatos = self.env['hr.applicant'].search_count([('curso_habilitacion','=',self.curso_id.id),('estado','=','proceso')])
             if candidatos == 0:
                 raise ValidationError(_("No existen candidatos a verificar para ese Curso de Habilitación !!"))


    @api.multi
    def print_report(self):

        datas = {
            'curso_id': self.curso_id.id,

        }

        return self.env['report'].get_action(self, 'app_seleccion.xls_report_vcurso', data=datas)

