# -*- coding: utf-8 -*-

{
    'name': 'DOWNLOAD FILE WIDGET',
    'summary': 'Needed in order to download a file from a form button...',
    'description': """
DOWNLOAD FILE WIDGET
====================

Needed in order to download a file from a form button...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': '',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'base',
        'web'
    ],

    # Always loaded.
    'data': [
        # Templates...
        'static/src/xml/download_file_widget_templates.xml',
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'qweb': [
        'static/src/xml/templates.xml'
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
