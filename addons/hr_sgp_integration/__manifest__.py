# -*- coding: utf-8 -*-

{
    'name': 'Módulo para la integración con SGP',
    'summary': 'Módulo para la integración con SGP',
    'description': """
Módulo para la integración con SGP
==========================

Módulo para la integración con SGP
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Tools',
    'version': '2.0',

    # Any module necessary for this one to work correctly.
    'depends': ['l10n_cu_hlg_hr', 'l10n_cu_hlg_db_external_connector'],

    # Always loaded.
    'data': [
        # Security...
        'security/ir.model.access.csv',

        # Data files to load...

        # Views...
        'views/hr_sgp_integration_views.xml',
        'wizard/import_config_wizard_view.xml'
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
