# -*- coding: utf-8 -*-

{
    'name': 'Simple Product',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'summary': 'This is an alternative module for managing products...',
    'description': """
Simple Product
===============

This is a module for the managing products, avoiding the complexity of the original module of Odoo...
    """,
    'category': 'Products',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': ['product'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views...
        'views/main_menus.xml',
        'views/product_view.xml',
        'views/product_category_menus.xml',
        # 'views/product_uom_view.xml',
        'views/product_group_view.xml',

        # Templates...
        # 'static/src/xml/web_client_templates.xml',
    ],
    'installable': True,
    'application': True,
}
