# -*- coding: utf-8 -*-
{
    'name': 'Hr Turei',
    'version': '18.0',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Human Resources',
    "license": "LGPL-3",
    'sequence': 5,
    'summary': 'Customizing the employee module for the Lázaro Peña Cigar Company. Holguín, Cuba',
    'description': """
Hr Turei
=========

Customizing the employee module for the Lázaro Peña Cigar Company. Holguín, Cuba.
    """,
    'depends': ['hr', 'resource', 'hr_recruitment'],
    'auto_install': ['hr'],
    'data': [
        # Data
        'data/cron_data.xml',
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/hr_employee_views.xml',
        'views/res_user_views.xml',
        'views/hr_candidate_views.xml',
    ],
}