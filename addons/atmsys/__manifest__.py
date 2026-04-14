# -*- coding: utf-8 -*-

{
    'name': 'AtmSys',
    'summary': 'Sistema para el control del departamento de ATM de la Fab. Cigarros Lazaro Peña...',
    'description': """
AtmSys
======

Sistema para el control del departamento de ATM de la Fab. Cigarros Lazaro Peña...
    * Control de productos.
    * Control de almacenes e inventarios.
""",

    'author': "Alejandro Cora González",
    'website': "alek.cora.glez@gmail.com",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Inventory, Logistic, Storage',
    'version': '2.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        #'turei_maintenance',
        'atm_product',
        'versat_integration',
        'l10n_cu_base',
        'warehouse',
        'hr',
        'save_readonly_fields',
        'web_export_view',
        'hide_official_modules',
        'turei_maintenance',
    ],

    # Always loaded.
    'data': [
        # Security...
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data files to load...
        'data/work_order_type_data.xml',
        'data/product_destiny_data.xml',
        'data/configuration_data.xml',
        'data/ir_sequence_data.xml',

        # Views...
        'views/menu.xml',
        'views/work_order_view.xml',
        'views/warehouse_request_view.xml',
        'views/blind_reception_view.xml',
        'views/cost_center_budget_view.xml',
        'views/product_view.xml',
        'views/product_assignment_view.xml',
        'views/product_control_view.xml',
        'views/employee_view.xml',
        'views/destiny_views.xml',
        'views/production_plan_views.xml',
        'views/storeroom_existence_views.xml',
        'views/daily_production_views.xml',
	    'views/employee_driver_view.xml',
        'views/ir_sequence_view.xml',


        # Reports...
        'reports/report_paper_formats.xml',
        'reports/report_menu.xml',
        'reports/warehouse_products_request_report_template.xml',
        'reports/unloading_authorization_extend_report_template.xml',
        'reports/unloading_authorization_report_template.xml',
        'reports/extracted_resources_report_template.xml',

        'views/configuration_views.xml',

        # Wizards...
        'wizard/import_wizard_view.xml',
        'wizard/print_report_wizard_views.xml',
        'wizard/work_order_cancel_wizard_view.xml',

        # Templates...
        'static/src/xml/webclient_templates.xml',
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'qweb': [
        'static/src/xml/custom_download_file_widget_template.xml'
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
