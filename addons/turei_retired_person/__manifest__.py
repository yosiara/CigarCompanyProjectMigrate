# -*- coding: utf-8 -*-
{
    'name': 'Gestión de Jubilados',
    'summary': 'Sistema de Gestion de Jubilados',
    'description': """Sistema de Gestion de Jubilados """,

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': [
        'base',
        'l10n_cu_base',
        'l10n_cu_hlg_hr',
        'l10n_cu_report_docxtpl',
        'app_seleccion'
    ],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/ir.model.access.csv',

        # Data files to load...


        # Views definitions...
        'views/turei_retired_person_view.xml',

        # Reports definitions...
        'reports/turei_retired_report_retired_person.xml',


        # Wizards...
        'wizards/import_retired.xml',
        'wizards/update_retired_from_hr.xml',
        'wizards/turei_retired_wzd_retired_person.xml'
    ],

    # Only loaded in demonstration mode.
    'demo': [],
    'test': [],
    'gweb': [
        "static/src/xml/*.xml"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,

}
