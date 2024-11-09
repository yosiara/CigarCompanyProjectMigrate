# -*- coding: utf-8 -*-

{
    'name': 'Versat Integration',
    'summary': 'Used to make data import from Versat...',
    'description': """
Versat Integration
==================

Used to make data import from Versat.
Product information will be load to the tables of simple_product module...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': '',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'l10n_cu_hlg_db_external_connector',
        'simple_product',
        'warehouse',
    ],

    # Always loaded.
    'data': [
        # Data files to load...

        # Views...
        'views/versat_uom_view.xml',
        'views/product_movement_view.xml',
        'views/product_view.xml',
        'views/versat_concept_views.xml',
        'views/account_views.xml',

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
