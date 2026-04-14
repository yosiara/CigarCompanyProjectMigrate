# -*- coding: utf-8 -*-

{
    'name': 'Fastos Integration',
    'summary': 'Used to make data import from Versat...',
    'description': """
Fastos Integration
==================

Used to make data import from Fastos...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'hr',
    ],

    # Always loaded.
    'data': [
        # Data files to load...

        # Views...

        # Wizards...
        'wizard/import_wizard_view.xml',
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}