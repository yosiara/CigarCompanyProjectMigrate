# -*- coding: utf-8 -*-

{
    'name': 'ALTERNATIVE VISUAL THEME',
    'summary': 'Change the odoo visual theme...',
    'description': """ """,

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Visual Themes',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
    ],

    # Always loaded.
    'data': [
        # Templates...
        'static/src/xml/alternative_theme_templates.xml',
        'static/src/xml/webclient_templates.xml',
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
