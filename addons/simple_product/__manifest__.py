# -*- coding: utf-8 -*-

{
    'name': 'Products',
    'summary': 'This is an alternative module for managing products...',
    'description': """
Products
========

This is a module for the managing products, avoiding the complexity of the original module of Odoo...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Products',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'product',
    ],

    # Always loaded.
    'data': [
        # Data files to load...

        # Views...
        'views/menu.xml',
        'views/product_view.xml',
        'views/product_category_view.xml',
        'views/product_uom_view.xml',
        'views/product_group_view.xml',

        # Wizards...

        # Templates...
        'static/src/xml/web_client_templates.xml',
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
