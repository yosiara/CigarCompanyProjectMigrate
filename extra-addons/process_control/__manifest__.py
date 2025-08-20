# -*- coding: utf-8 -*-
{
    'name': 'Process Control',
    'version': '17.0',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Productivity',
    'license': 'LGPL-3',
    'sequence': 2,
    'summary': 'Control of the production process of the Lázaro Peña Cigar Factory. Holguín, Cuba',
    'description': """
Process Control
================

Control module for interruptions in the production process of the Lázaro Peña Cigar Factory.
Holguín, Cuba.
    """,
    'depends': ['mail'],
    'data': [
        #-----------------------data-------------------------------------#
        'data/machine_types.xml',
        'data/interruption_type.xml',
        'data/machine_set_of_peaces.xml',
        'data/turn.xml',

        #-----------------------security-------------------------------------#
        'security/process_control_groups.xml',
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
        # 'views/rechazo.xml',
        'views/rechazo_amf.xml',
        'views/rechazo_mod1.xml',
        'views/turn_attendance.xml',
        'views/production_by_hours.xml',

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
    'assets': {
        'web.assets_backend': [
            'process_control/static/src/core/report_handler.js',
            # 'process_control/static/src/views/**/*.js',
            # 'process_control/static/src/views/**/*.xml',
            # 'process_control/static/src/scss/**/*.scss',
            #'extra-addons/process_control/static/src/core/formAutoSave.js',
            #'process_control/static/src/css/fields.css',
        ],
    },
    'installable': True,
    'application': True,
}
