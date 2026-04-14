# -*- coding: utf-8 -*-

{
    'name': 'Stock Turei',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'summary': 'Customizing the native Stock module for turei...',
    'description': """
Stock Turei
============

Customizing the native Stock module for the Lazaro Peña Cigar Company...
    """,
    'category': 'Inventory',
    'version': '1.0',
    'license': 'LGPL-3',
    'sequence': 4,
    'depends': ['stock'],
    'data': [
        # Security
        # 'security/ir.model.access.csv',

        # Views...
        # 'views/main_menus.xml',
        # 'views/product_view.xml',
        # 'views/product_category_menus.xml',
        # # 'views/product_uom_view.xml',
        # 'views/product_group_view.xml',
        'views/product_product.xml',

        # Templates...
        # 'static/src/xml/web_client_templates.xml',
    ],
    'installable': True,
}
