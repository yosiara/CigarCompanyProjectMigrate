# -*- coding: utf-8 -*-

{
    'name': 'External Database Connector',
    'summary': 'Used to make connections to external databases...',
    'description': """
External Database Connector.
============================

Used to make connections to external databases...
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Database Connector',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'base',
        'mail',
    ],

    # Always loaded.
    'data': [
        # Data files to load...
        'views/menu_view.xml',
        'views/external_db_source_view.xml',
        'security/db_external_connector_security.xml',
        'security/ir.model.access.csv',
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