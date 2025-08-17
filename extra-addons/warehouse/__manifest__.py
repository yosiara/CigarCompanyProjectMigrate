# -*- coding: utf-8 -*-

{
    'name': 'Warehouse',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Inventory',
    'version': '1.0',
    'summary': 'This is an alternative module for managing product inventory...',
    'description': """
Warehouse
==========

This is a module for the managing products, avoiding the complexity of the original module of Odoo...
    """,
    'depends': [
        'simple_product',
        'hr',
    ],
    'data': [
        # Views...
        'views/warehouse_view.xml',
        'views/product_control_view.xml',
        'views/product_view.xml',
        'views/warehouse_request_view.xml',
        'views/employee_view.xml',
        'views/employee_driver_view.xml',
    ],
    'installable': True,
}
