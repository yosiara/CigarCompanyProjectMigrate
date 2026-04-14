# -*- coding: utf-8 -*-

{
    'name': 'Human Resources for CUBA',
    'summary': '',
    'description': """
Human Resources for CUBA
========================

Adding elements to the HR module of Odoo, needed for all HR modules in l10n_cu localization
    * Positions
    * Occupational category
    * Salary scale
    * Salary group
    * Security rules
    * Aditional fields on employee, jobs and departments
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Human Resources',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': [
        'l10n_cu_base',
        'product',
        'hr',
    ],

    # Always loaded.
    'data': [
        # Security and groups...
        'security/l10n_cu_hr_security.xml',
        'security/ir.model.access.csv',

        # Data files to load...
        'data/l10n_cu_hlg_hr_data.xml',

        # Views definitions...
        'views/resource_views.xml',
        'views/l10n_cu_hlg_hr_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_department_views.xml',
        'views/hr_employee_school_level_views.xml',
        'views/hr_job_occupational_category_views.xml',
        'views/hr_job_salary_group_views.xml',
        'views/hr_employee_config_settings_views.xml',
        'views/hr_board_views.xml',
        'views/res_base_view.xml',
        'wizard/report_registrarion_attendance_wzd_view.xml',
        'wizard/report_registration_attendance.xml',

        # Wizards...
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
