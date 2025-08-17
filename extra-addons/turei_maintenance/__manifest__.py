# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Industrial Maintenance',
    'version': '1.0',    'author': 'Desoft. Holguín. Cuba.',
    'category': 'Turei',
    # 'sequence': 20,

    'summary': 'Módulo de control del Proceso de Mantenimiento Industrial de la Fábrica de Cigarros Lázaro Peña.',
    'description': "Módulo de control del Proceso de Mantenimiento Industrial de la Fábrica de Cigarros Lázaro Peña.",
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['report','report_xlsx','maintenance', 'l10n_cu_base', 'warehouse'],
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
        'reports/report_paper_formats.xml',
        'reports/report_menu.xml',
        'reports/work_order_report_template.xml',
        'reports/resources_consumed_report.xml',
        'reports/orders_delivered_report.xml',
        'reports/orders_no_delivered_report.xml',
        'reports/orders_planned_report.xml',
        'reports/orders_pending_report.xml',
        'reports/equipment_report_template.xml',
        'reports/equipment_parts_report.xml',
        'reports/plan_mtto_report.xml',
        'reports/efficacy_evaluation_report.xml',
        'reports/work_maint_team_report.xml',
        'reports/work_type_work_report.xml',
        'reports/request_maint_report.xml',

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
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
}
