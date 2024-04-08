# -*- coding: utf-8 -*-

{
    'name': 'Base for CU localization',
    'summary': '',
    'description': """
Base extension.
===============

Adiciona elementos al kernel de Odoo,necesarios para los módulos de l10n_cu localization...
""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Localization',
    'version': '1.0',

    # Any module necessary for this one to work correctly.
    'depends': [
        'base',
        'resource',
        'inputmask_widget',
        'report',
        'web_notify',
        'l10n_cu_hlg_single_login','l10n_cu_report_docxtpl'
    ],

    # Always loaded.
    'data': [
        # Data files to load...
        'data/res_country_states_data.xml',
        'data/report_paperformat_data.xml',

		# Views...
        'views/res_partner_view.xml',
        'views/res_partner_bank_view.xml',

        'views/webclient_templates.xml',
        'views/res_company_view.xml',
        'views/res_country_view.xml',
        'views/res_users_view.xml',
        'views/ir_mail_server_view.xml',
        'views/area_view.xml',
        'views/cost_center_view.xml',
        'views/responsibility_area_view.xml',

        'security/ir.model.access.csv',

        'report/report_customer_template.xml',
        'report/report_partners_file_empty.xml',
        'report/report_partners_file.xml',
        #'report/report.xml',
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
