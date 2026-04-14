# -*- coding: utf-8 -*-

{
    'name': 'ATM Products',
    'summary': 'To inherit the original product module and make the necessary corrections...',
    'description': """
ATM Products
============

To inherit the original Product module and make the necessary corrections...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Sales',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'simple_product',
    ],

    # Always loaded.
    'data': [
        # Data files to load...

        # Views...
        'views/product_view.xml',
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
