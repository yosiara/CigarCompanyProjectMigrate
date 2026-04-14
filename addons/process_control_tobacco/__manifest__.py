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
    'name': 'ControlPros Tobacco',
    'version': '0.9',
    'author': 'Desoft. Holguín. Cuba.',
    'category': 'Turei',
    # 'sequence': 20,

    'summary': 'Módulo de control de las interrupciones en el Departamento de Producción de Tabaco Reconstituido de la Fábrica de Cigarros Lázaro Peña.',
    'description': "Módulo de control de las interrupciones en el Departamento de Producción de Tabaco Reconstituido de la Fábrica de Cigarros Lázaro Peña.",
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['resource', 'report', 'tree_formula_parser', 'auditlog', 'web_notify', 'report_xlsx'],
    'data': [
        'data/machine_types.xml',
        'data/interruption_type.xml',

        'security/tobacco_security.xml',
        'security/ir.model.access.csv',

        'views/base_menu.xml',
        'views/machine_type.xml',
        'views/interrution_type.xml',
        'views/interruptions.xml',
        'views/control_model.xml',
        'views/dashboard.xml',
        'views/turn.xml',

        'wizard/wzd_interruption.xml',
        'wizard/wzd_use_of_time.xml',
        'wizard/wzd_summary_time_frequency.xml',
        'wizard/wzd_production_hours.xml',
        'wizard/wzd_flow_lines.xml',
        'wizard/wzd_efficiency_ltr.xml',

        'reports/interruption_report.xml',
        'reports/use_of_time_report.xml',
        'reports/summary_time_frequency_report.xml',
        'reports/production_hours_report.xml',
        'reports/flow_lines_report.xml',
        'reports/efficiency_ltr_report.xml',

        

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
