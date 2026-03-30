# -*- coding: utf-8 -*-
{
    'name': 'Calendar Turei',
    'version': '18.0',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Productivity/Calendar',
    'license': 'LGPL-3',
    'sequence': 166,
    'summary': 'Customizing the calendar module for the Lázaro Peña Cigar Company. Holguín, Cuba',
    'description': """
Calendar Turei
===============

Customizing the calendar module for the Lázaro Peña Cigar Company. Holguín, Cuba.
    """,
    'depends': ['calendar', 'hr'],
    'auto_install': ['calendar'],
    'data': [
        'security/calendar_turei_security.xml',
        'security/ir.model.access.csv',

        'views/calendar_views.xml',
        'views/organizational_groups.xml',
        'views/periods.xml',

        'reports/individual_plan_report.xml',

        'wizard/individual_plan_view.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'calendar_turei/static/src/views/calendar_filter_panel.js',
        ]
    }
}