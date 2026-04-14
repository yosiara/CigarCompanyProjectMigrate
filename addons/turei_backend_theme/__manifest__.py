# -*- coding: utf-8 -*-

{
    'name': 'TUREI BACKEND THEME',
    'summary': 'Backend theme...',
    'description': """
BACKEND THEME
=============

Backend theme...
""",

    'author': "Desoft Holguin",
    'website': "",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Turei',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'web_settings_dashboard',
        'web',
    ],

    # Always loaded.
    'data': [
        # Templates...
        'data/datas.xml',
        'templates/webclient_template.xml',
        'templates/turei_backend_theme_templates.xml',
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],
    'qweb': ['static/src/xml/dashboard.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
