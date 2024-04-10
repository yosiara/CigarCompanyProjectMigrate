# -*- coding: utf-8 -*-

{
    'name': 'PC-Inside v1.1',
    'summary': 'Sistema que gestiona varias de las acciones que se realizan en el área de informática. Resaltando la Seguridad Informática.',
    'description': """
Computers Inventory
===================

Computers Inventory using OCS Inventory Server...
    * Server Version: 2.3.1...
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Tools',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'l10n_cu_hlg_db_external_connector',
        #'l10n_cu_report_docxtpl',
        'hr_maintenance',
        'maintenance',
        #'l10n_cu_base',
        #'l10n_cu_locals',
    ],

    # Always loaded.
    'data': [
        # Security...
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data...
        'data/configuration_data.xml',
        'data/computers_inventory_cron_data.xml',

        # Report...
        'reports/external_layout.xml',
        'reports/paper_formats.xml',
        'reports/report_inventory.xml',
        'reports/reports.xml',
        'reports/report_inspection.xml',
        'reports/report_security_incident.xml',
        'reports/report_control_applications.xml',
        'reports/report_saves.xml',
        'reports/report_audit_plan.xml',
        'reports/report_equipment_label.xml',
        'reports/report_authorized_software.xml',
        'reports/report_system_service_application.xml',

        # Views definitions...
        'views/menu.xml',
        'views/menu_records.xml',
        'views/menu_reports.xml',
        'views/maintenance_equipment_component_views.xml',
        'views/equipment_component_movement_views.xml',
        'views/maintenance_equipment_views.xml',
        'views/configuration_views.xml',
        'views/audit_views.xml',
        'views/security_incident_views.xml',
        'views/permissions_views.xml',
        'views/inspection_views.xml',
        'views/work_order_views.xml',


        # Wizards...
        'wizards/import_wizard_views.xml',
        'wizards/l10n_cu_hlg_computers_inventory_registry_information_view.xml',
        'wizards/wzd_report_inspection.xml',
        'wizards/wzd_report_security_incident.xml',
        'wizards/control_applications_wzd_views.xml',
        'wizards/saves_wzd_views.xml',
        'wizards/wzd_report_audit_plan.xml',
        'wizards/create_order_wzd_views.xml',
        'wizards/approve_movements_wzd_views.xml',

        # Templates...
        'static/src/xml/webclient_templates.xml',
    ],

    # Only loaded in demonstration mode.
    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
    "post_init_hook": "post_init_hook",
}
