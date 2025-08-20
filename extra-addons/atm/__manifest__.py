# -*- coding: utf-8 -*-

{
    'name': 'ATM',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'license': 'LGPL-3',
    'category': 'Inventory',
    'version': '2.0',
    'sequence': 3,
    'summary': 'System for controlling the ATM department of the Lázaro Peña Cigar Company...',
    'description': """
ATM
====

System for controlling the ATM department of the Lázaro Peña Cigar Company...
    * Product control.
    * Warehouse and inventory control.
    """,
    'depends': [
        'hr',
        'warehouse',
        'simple_product',
        'maintenance_turei',
        # 'versat_integration',
        # 'save_readonly_fields',
        # 'web_export_view',
        # 'hide_official_modules',
    ],
    'data': [
        # Security...
        # 'security/security.xml',
        # 'security/ir.model.access.csv',

        # Data files to load...
        'data/work_order_type_data.xml',
        'data/product_destiny_data.xml',
        # 'data/configuration_data.xml',
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
        'views/configuration_views.xml',

        # Reports...
        'reports/report_paper_formats.xml',
        'reports/report_menu.xml',
        'reports/warehouse_products_request_report_template.xml',
        'reports/unloading_authorization_extend_report_template.xml',
        'reports/unloading_authorization_report_template.xml',
        'reports/extracted_resources_report_template.xml',

        # Wizards...
        'wizard/import_wizard_view.xml',
        # 'wizard/print_report_wizard_views.xml',
        'wizard/work_order_cancel_wizard_view.xml',

        # Templates...
        'static/src/xml/webclient_templates.xml',
    ],
    'qweb': [
        'static/src/xml/custom_download_file_widget_template.xml'
    ],
    'installable': True,
    'application': True,
}
