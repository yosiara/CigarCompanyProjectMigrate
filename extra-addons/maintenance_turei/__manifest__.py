# -*- coding: utf-8 -*-

{
    'name': 'Maintenance Turei',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Manufacturing',
    'version': '1.0',
    'sequence': 4,
    'license': 'LGPL-3',
    'summary': 'Control module of the Industrial Maintenance Process of the Lázaro Peña Cigar Company.',
    'description': """
Maintenance Turei
==================

Control module of the Industrial Maintenance Process of the Lázaro Peña Cigar Company.
    """,
    'depends': ['maintenance', 'base_cu', 'warehouse'],
    'data': [
        # Security...
        'security/security.xml',
        'security/ir.model.access.csv',

        # Data files to load...
        'data/line.xml',
        'data/efficacy_evaluation.xml',

        # Views...
        'views/menu.xml',
        'views/work_order_view.xml',
        'views/maintenance_views.xml',
        'views/equipment_parts.xml',
        'views/incident_plan.xml',
        'views/equipment_electric_motor.xml',
        'views/line_views.xml',
        'views/efficacy_evaluation_views.xml',

        # Reports...
        # 'reports/report_paper_formats.xml',
        # 'reports/report_menu.xml',
        # 'reports/work_order_report_template.xml',
        # 'reports/resources_consumed_report.xml',
        # 'reports/orders_delivered_report.xml',
        # 'reports/orders_no_delivered_report.xml',
        # 'reports/orders_planned_report.xml',
        # 'reports/orders_pending_report.xml',
        # 'reports/equipment_report_template.xml',
        # 'reports/equipment_parts_report.xml',
        # 'reports/plan_mtto_report.xml',
        # 'reports/efficacy_evaluation_report.xml',
        # 'reports/work_maint_team_report.xml',
        # 'reports/work_type_work_report.xml',
        # 'reports/request_maint_report.xml',

        # Wizards...
        'wizard/wzd_resources_consumed.xml',
        'wizard/wzd_orders_delivered.xml',
        'wizard/wzd_orders_no_delivered.xml',
        'wizard/wzd_orders_planned.xml',
        'wizard/wzd_orders_pending.xml',
        'wizard/wzd_equipment_parts.xml',
        'wizard/wzd_plan_mtto.xml',
        'wizard/wzd_generate_plan_mtto.xml',
        'wizard/import_wizard_view.xml',
        'wizard/config_maintenance_view.xml',
        'wizard/config_work_order_view.xml',
        'wizard/wzd_efficacy_evaluation.xml',
        'wizard/wzd_work_maint_team.xml',
        'wizard/wzd_work_type_work.xml',
        'wizard/wzd_request_maint.xml',

    ],
    'installable': True,
}
