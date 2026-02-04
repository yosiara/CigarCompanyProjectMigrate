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
    'depends': ['hr'],
    'auto_install': ['hr'],
    'data': [
        #-----------------------data----------------------------------------#
        'data/cron_data.xml',
        #-----------------------views----------------------------------------#
        'views/hr_employee.xml',
        'views/res_user.xml',
    ],
}