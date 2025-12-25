# -*- coding: utf-8 -*-
{
    'name': 'Planning Turei',
    'version': '18.0',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Human Resources/Planning',
    "license": "LGPL-3",
    'sequence': 131,
    'summary': 'Customizing the Planning module for the Lázaro Peña Cigar Company. Holguín, Cuba',
    'description': """
Planning Turei
=================

Customizing the Planning module for the Lázaro Peña Cigar Company. Holguín, Cuba.
    """,
    'depends': ['planning', 'mail'],
    'auto_install': ['planning'],
    'data': [
        # ---------------------- security ------------------------------------#
        'security/ir.model.access.csv',
        #----------------------- data ----------------------------------------#
        'data/planning_slot_data.xml',
        'data/mail_template_data.xml',
        'data/mail_templates_email_layouts.xml',
        #----------------------- views ---------------------------------------#
        'views/planning.xml',
        'views/prorogation.xml',
        'views/subcommissions.xml',
    ],
}