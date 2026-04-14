# -*- coding: utf-8 -*-

{
    'name': 'Hide Official Modules',
    'summary': 'To hide official modules from the module list...',
    'description': """
Hide Official Modules
=====================

...
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
    ],

    # Always loaded.
    'data': [
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
