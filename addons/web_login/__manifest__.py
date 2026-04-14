# -*- coding: utf-8 -*-

{
    'name': 'WEB LOGIN SCREEN',
    'summary': 'Change the web login template...',
    'description': """
WEB LOGIN SCREEN
================

Change the web login template...
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Website',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'web',
    ],

    # Always loaded.
    'data': [
        # Templates...
        'templates/web_client_templates.xml',
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
