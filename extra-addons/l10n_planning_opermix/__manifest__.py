# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Planning Empresa de Cigarros",
    'summary': """Manage your employees' schedule""",
    'description': """
Schedule your teams and employees with shift.
    """,
    'category': 'Human Resources/Planning',
    'sequence': 131,
    'version': '1.0',
    'depends': ['planning'],
    'data': [
        # 'security/planning_security.xml',
        'security/ir.model.access.csv',
        # 'data/digest_data.xml',
        # 'wizard/planning_send_views.xml',
        # 'views/hr_views.xml',
        # 'views/planning_template_views.xml',
        # 'views/resource_views.xml',
        'views/planning_views.xml',
        # 'views/planning_report_views.xml',
        # 'views/res_config_settings_views.xml',
        # 'views/planning_templates.xml',
        # 'report/planning_report_templates.xml',
        # 'report/planning_report_views.xml',
        # 'data/planning_cron.xml',
        # 'data/mail_template_data.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
