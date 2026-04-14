# -*- coding: utf-8 -*-

{
    'name': 'HR Import (Fastos Integration)',
    'summary': 'Import to Odoo important information from FastosPagus Database...',
    'description': """
HR Import.
==========

Import to Odoo important information from FastosPagus Database. Features are:
    * Import employee directory.
    * Import work employee's work time.

    *Function for cron
        OBJECT l10n_cu_hr_import.import_employee_wizard
        - action_import_function ()
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'l10n_cu_hlg_db_external_connector',
        'hr_turei',
        'l10n_cu_hlg_cron',
    ],

    # Always loaded.
    'data': [
        # Data files to load...
        'data/l10n_cu_hlg_hr_data.xml',

        # Views definitions...

        # Wizards...
        'wizard/import_wizard_view.xml',
        'wizard/attendance_import_wzd_view.xml',
        'wizard/import_employee_code_view.xml',
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
