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
    'name': 'Process Control',
    'version': '17.0',
    'author': 'Yosiel Arango Arencibia',
    'category': 'Turei',
    "license": "LGPL-3",
    'sequence': 2,
    'summary': 'Control of the production process of the Lázaro Peña Cigar Factory. Holguín, Cuba',
    'description': """Control module for interruptions in the production process of the Lázaro Peña Cigar Factory. 
    Holguín, Cuba.""",
    'images': [],
    'depends': ['mail'],
    'data': [
        #-----------------------data-------------------------------------#
        'data/machine_types.xml',
        'data/interruption_type.xml',
        'data/machine_set_of_peaces.xml',
        'data/turn.xml',
        # 'security/turei_security.xml',
        # 'security/ir.model.access.csv',
        'security/ir.model.access.csv',

        #-----------------------views-------------------------------------#
        'views/base_menu.xml',
        'views/turn.xml',
#        'views/db_production_connector.xml',
        'views/machine_type.xml',
        'views/machine.xml',
        'views/interrution_type.xml',
        'views/interruption.xml',
        'views/productive_line.xml',
        'views/productive_section.xml',
        'views/machine_set_of_peaces.xml',
        'views/tecnolog_control.xml',
        'views/productive_section_plan.xml',
        'views/dashboard.xml',

        #-----------------------wizard-------------------------------------#
        'wizard/interruptions_pdf_wzd.xml',
        'wizard/interruptions_excel_wzd.xml',
        'wizard/compliance_planned_cdt_wzd.xml',
        # 'wizard/efficient_report_wzd.xml',
        # 'wizard/production_by_hours_wzd.xml',
        # 'wizard/interruptions_by_line_wzd.xml',
        # 'wizard/interruptions_by_machine_wzd.xml',
        # 'wizard/efficiency_accomplish_wzd.xml',
        # 'wizard/prod_and_reg_amf_wzd.xml',
        # 'wizard/time_to_excel_wzd.xml',
        # 'wizard/efficiency_cdt_excel_report_wzd.xml',
        # #'wizard/resume_time_frequency_wzd.xml',
        # 'wizard/compliance_planned_efficiency_wzd.xml',
        # 'wizard/machine_set_of_peaces_wzd.xml',
        # 'wizard/bd_production_hours_wzd.xml',
        # 'wizard/statistical_results_wzd.xml',
        # 'wizard/production_rejection_wzd.xml',
        # 'wizard/resume_time_frequency_n_wzd.xml',

        #-----------------------reports------------------------------------#
        'reports/pdf/interruptions_pdf_report.xml',
        # 'reports/efficient_report.xml',
        # 'reports/production_by_hours_report.xml',
        # 'reports/interruptions_by_line_report.xml',
        # 'reports/interruptions_by_machine_report.xml',
        # 'reports/efficiency_accomplish_report.xml',
        # 'reports/prod_and_reg_amf_report.xml',
        # 'reports/interruptions_to_excel_report.xml',
        # 'reports/time_use_to_excel_report.xml',
        # 'reports/efficiency_cdt_excel_report.xml',
        # 'reports/resume_time_frequency_report.xml',
        # 'reports/compliance_planned_efficiency.xml',
        #'reports/xlsx/compliance_planned_cdt.xml',
        # 'reports/machine_set_of_peaces_report.xml',
        # 'reports/bd_production_hours_report.xml',
        # 'reports/statistical_results_report.xml',
        # 'reports/production_rejection_report.xml',
        # 'reports/resume_time_frequencyn_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
    'assets': {
        'web.assets_backend': [
            'process_control/static/src/js/report_handler.js',
        ],
    },
}
