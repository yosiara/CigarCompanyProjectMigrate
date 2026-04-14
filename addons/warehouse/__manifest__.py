# -*- coding: utf-8 -*-

{
    'name': 'Warehouse',
    'summary': 'This is an alternative module for managing product inventory...',
    'description': """
Warehouse
=========

This is a module for the managing products, avoiding the complexity of the original module of Odoo...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Inventory, Logistic, Storage',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'simple_product',
        'hr',
    ],

    # Always loaded.
    'data': [
        # Data files to load...

        # Views...
        'views/warehouse_view.xml',
        'views/product_control_view.xml',
        'views/product_view.xml',
        'views/warehouse_request_view.xml',
        'views/employee_view.xml',
        'views/employee_driver_view.xml',
        # Wizards...
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
