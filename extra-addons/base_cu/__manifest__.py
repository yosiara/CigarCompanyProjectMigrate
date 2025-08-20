# -*- coding: utf-8 -*-

{
    'name': 'Base CU',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'summary': 'Adds elements to the Odoo kernel, necessary for the l10n_cu localization modules',
    'description': """
Base extension.
================

Adds elements to the Odoo kernel, necessary for the l10n_cu localization modules...
    """,
    'category': 'Technical',
    'version': '1.0',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'resource',
        # 'web_notify',
        #'inputmask_widget',
        #'report',
        #'l10n_cu_hlg_single_login','l10n_cu_report_docxtpl'
    ],
    'data': [
        # Data files to load...
        'data/res_country_states_data.xml',
        'data/report_paperformat_data.xml',

		# Views...
        'views/res_partner_view.xml',
        # 'views/res_partner_bank_view.xml',

        # 'views/webclient_templates.xml',
        # 'views/res_company_view.xml',
        # 'views/res_country_view.xml',
        # 'views/res_users_view.xml',
        # 'views/ir_mail_server_view.xml',
        'views/area_view.xml',
        'views/cost_center_view.xml',
        'views/responsibility_area_view.xml',

        # Security
        'security/ir.model.access.csv',

        # 'report/report_customer_template.xml',
        # 'report/report_partners_file_empty.xml',
        # 'report/report_partners_file.xml',
        #'report/report.xml',
    ],
    'installable': True,
}
