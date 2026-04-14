# -*- coding: utf-8 -*-
{
    'name': 'uForce',
    'summary': 'Sistema de Gestion de la Fuerza de Trabajo Calificada',
    'description': """Sistema de Gestion de la Fuerza de Trabajo Calificada""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': [
        'l10n_cu_base',
        'l10n_cu_hlg_hr',
        'l10n_cu_hlg_hr_contract',
        # 'l10n_cu_hlg_hr_recruitment',
        'l10n_cu_hlg_hr_import',
        'l10n_cu_period',
        'l10n_cu_report_docxtpl'
    ],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/l10n_cu_hlg_uforce_security.xml',
        'security/ir.model.access.csv',

        # Data files to load...
        'data/ir_cron_data.xml',
        'data/school_level_data.xml',
        'data/age_range_data.xml',
        'data/contract_type_data.xml',
        'data/employment_data.xml',
        'data/l10n_cu_ministry_data.xml',
        'data/l10n_cu_hlg_uforce_data.xml',
        #'data/l10n_cu_period_data.xml',
        'data/res_country_state_data.xml',

        # Views definitions...
        'views/l10n_cu_hlg_uforce_view.xml',
        'views/hr_employee_view.xml',
        'views/res_partner_view.xml',

        # Reports definitions...
        'reports/l10n_cu_hlg_uforce_reports.xml',

        # Wizards...
        'wizards/registry_information_view.xml',
        'wizards/import_wizard_view.xml',
        'wizards/update_from_gforza_wizard_view.xml',
        'wizards/import_employees_excel_view.xml',
        'wizards/update_dpa_wzd_view.xml',
        'wizards/report_wzd_view.xml',
        'wizards/update_employee_age_range_wzd_view.xml'
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
    "post_init_hook": "post_init_hook",
}
