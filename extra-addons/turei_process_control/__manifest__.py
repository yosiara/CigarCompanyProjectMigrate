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
    'name': 'Turei ControlPros',
    'version': '0.9',
    'author': 'Desoft. Holguín. Cuba.',
    'category': 'Turei',
    # 'sequence': 20,

    'summary': 'Módulo de control de las interrupciones  en el proceso productivo de la Fábrica de Cigarros Lázaro Peña.',
    'description': "Módulo de control de las interrupciones  en el proceso productivo de la Fábrica de Cigarros Lázaro Peña.",
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['resource', 'report', 'tree_formula_parser', 'auditlog', 'web_notify', 'report_xlsx'],
    'data': [
        'data/machine_types.xml',
        'data/interruption_type.xml',
        'data/set_of_peaces.xml',
        'security/turei_security.xml',
        'security/ir.model.access.csv',

        'views/base_menu.xml',
        'views/db_production_connector.xml',
        'views/turn.xml',
        'views/machine_type.xml',
        'views/machine.xml',
        'views/interrution_type.xml',
        'views/interruptions.xml',
        'views/productive_line.xml',
        'views/productive_section.xml',
        'views/set_of_peaces.xml',
        'views/control_model.xml',
        'views/productive_section_plan.xml',
        'views/dashboard.xml',

        'wizard/wzd_efficient_report.xml',
        'wizard/wzd_production_by_hours.xml',
        'wizard/wzd_interruptions_by_section.xml',
        'wizard/wzd_interruptions_by_line.xml',
        'wizard/wzd_interruptions_by_machine.xml',
        'wizard/wzd_efficiency_accomplish.xml',
        'wizard/wzd_prod_and_reg_amf.xml',
        'wizard/wzd_interruptions_to_excel.xml',
        'wizard/wzd_time_to_excel.xml',
        'wizard/wzd_efficiency_cdt_excel_report.xml',
        #'wizard/wdz_resume_time_frequency.xml',
        'wizard/wdz_compliance_planned_efficiency.xml',
        'wizard/wdz_compliance_planned_cdt.xml',
        'wizard/wzd_machine_set_of_peaces.xml',
        'wizard/wzd_bd_production_hours.xml',
        'wizard/wzd_statistical_results.xml',
        'wizard/wzd_production_rejection.xml',
        'wizard/wdz_resume_time_frequency_n.xml',


        'reports/efficient_report.xml',
        'reports/production_by_hours_report.xml',
        'reports/interruptions_by_section_report.xml',
        'reports/interruptions_by_line_report.xml',
        'reports/interruptions_by_machine_report.xml',
        'reports/efficiency_accomplish_report.xml',
        'reports/prod_and_reg_amf_report.xml',
        'reports/interruptions_to_excel_report.xml',
        'reports/time_use_to_excel_report.xml',
        'reports/efficiency_cdt_excel_report.xml',
        #'reports/resume_time_frequency_report.xml',
        'reports/compliance_planned_efficiency.xml',
        'reports/compliance_planned_cdt.xml',
        'reports/machine_set_of_peaces_report.xml',
        'reports/bd_production_hours_report.xml',
        'reports/statistical_results_report.xml',
        'reports/production_rejection_report.xml',
        'reports/resume_time_frequencyn_report.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
