# -*- coding: utf-8 -*-

{
    'name': 'Defense information',
    'summary': '',
    'description': """
Human Resources Defense information
========================

""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': [ 'l10n_cu_hlg_hr'],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/ir.model.access.csv',

        # Views definitions...
        'view/hr_defense_inf_views.xml',

         # Views definitions...
        'reports/defense_report.xml',

        # Wizards...
        'wizard/wizard_view.xml'
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

