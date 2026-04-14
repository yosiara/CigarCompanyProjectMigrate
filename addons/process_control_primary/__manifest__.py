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

{
    'name': 'ControlPros Primary',
    'version': '0.9',
    'author': 'Desoft. Holguín. Cuba.',
    'category': 'Turei',
    # 'sequence': 20,

    'summary': 'Módulo de control de las interrupciones en el taller primario en el proceso productivo de la Fábrica de Cigarros Lázaro Peña.',
    'description': "Módulo de control de las interrupciones en el taller primario en el proceso productivo de la Fábrica de Cigarros Lázaro Peña.",
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['resource', 'report', 'tree_formula_parser', 'auditlog', 'web_notify', 'report_xlsx'],
    'data': [
        'data/machine_types.xml',
        'data/interruption_type.xml',
        'security/primary_security.xml',
        'security/ir.model.access.csv',

        'views/base_menu.xml',
        'views/machine_type.xml',
        'views/interrution_type.xml',
        'views/interruptions.xml',
        'views/productive_line.xml',
        'views/control_model.xml',
        'views/dashboard.xml',

        'wizard/wzd_efficiency_dph.xml',
        'wizard/wzd_interruption.xml',
        'wizard/wzd_use_of_time.xml',
        'wizard/wzd_flow_by_lines.xml',
        'wizard/wzd_efficiency_cdt_dph.xml',
        'wizard/wzd_summary_time_frequency.xml',

        'reports/efficiency_dph_report.xml',
        'reports/interruption_report.xml',
        'reports/use_of_time_report.xml',
        'reports/flow_by_lines_report.xml',
        'reports/efficiency_cdt_dph_report.xml',
        'reports/summary_time_frequency_report.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
