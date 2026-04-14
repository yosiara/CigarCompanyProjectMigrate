# -*- coding: utf-8 -*-
{
    'name': 'Sistema de Gestión de la Capacitación',
    'summary': 'Sistema de Gestión de la Capacitación',
    'description': """Sistema de Gestión de la Capacitación """,

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
        'app_seleccion',
        'l10n_cu_hlg_uforce'
    ],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/ir.model.access.csv',

        # Data files to load...
        'data/capacitation_data.xml',

        # Views definitions...
        'views/turei_capacitacion_view.xml',

        # Reports definitions...
        'reports/turei_capacitacion_plan.xml',
        'reports/turei_capacitation_plan_individual.xml',


        # Wizards...
        'wizards/turei_capacitation_wzd_plan.xml',

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
