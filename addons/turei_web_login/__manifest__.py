# -*- coding: utf-8 -*-

{
    'name': 'TUREI WEB LOGIN',
    'summary': '',
    'description': "",
    'category': 'Turei',

    'author': "Desoft Holguin",
    'website': "",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Turei',
    'version': '1.1.2',

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

    'installable': True,
    'application': False,
    'auto_install': False,
}
