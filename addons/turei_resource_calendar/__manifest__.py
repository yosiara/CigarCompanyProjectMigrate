# -*- coding: utf-8 -*-

{
    'name': 'Working Calendar additions',
    'summary': 'Some additions to standard Working Calendar',
    'description': """
This module allow create irregular Working Calendars like
Repeat this cycle finding the corresponding working dates
""",
    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': [
        'hr_sgp_integration'
        ],

    # Always loaded.
    'data': [
        'security/ir.model.access.csv',
        'view/l10n_cu_hlg_resource_calendar_view.xml',
    ],

    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

