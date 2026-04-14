# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Contratación de Clientes y Proveedores (Mentor v3.1)',
    'version': '3.1',
    'summary': 'Sistema de Contratación de Clientes y Proveedores.',
    'sequence': 30,
    'description': """
    Sistema para gestionar la contratación económica con Clientes y Proveedores. Se basa en los Decreto Ley No. 304 y el Decreto 310 del 2012 de la Contratación económica.

    """,
    'category': 'Sale',
    'website': 'http://www.desoft.cu',
    'author': "Desoft. Holguín. Cuba.",
    'images': [],
    'depends': ['l10n_cu_base', 'sale', 'hr', 'purchase', 'crm', 'download_file_widget', 'document', 'report_xlsx','l10n_cu_report_docxtpl','l10n_cu_locals','web_widget_timepicker'],
    'data': [
        'security/l10n_cu_contract_security.xml',
        'security/ir.model.access.csv',
        'security/l10n_cu_contract_rule_security.xml',

        'views/contract_menu_view.xml',
        'views/contract_type_view.xml',
        'views/contract_view.xml',
        'views/contract_committee_view.xml',
        'views/sale_view.xml',
        'views/partner_view.xml',
        'views/contract_dashboard_view.xml',
        'views/dashboard.xml',
        'views/config_parameter_view.xml',
        'views/ir_sequence_view.xml',

        'wizard/l10n_cu_contract_print_registry_view.xml',
        'wizard/l10n_cu_contract_registry_information_view.xml',
        'wizard/l10n_cu_contract_create_sale_order_view.xml',
        'wizard/l10n_cu_contract_to_expire_view.xml',
        'wizard/l10n_cu_contract_to_expire_percent_view.xml',
        'wizard/l10n_cu_contract_hiring_status_view.xml',
        'wizard/l10n_cu_contract_close_expired_view.xml',


        'data/contract_email_template_data.xml',
        'data/ir_cron_data.xml',
        'data/dashboard_data.xml',
        'data/ir_config_parameter_view.xml',
        'data/ir_sequence_data.xml',

        'report/report_paper_formats.xml',
        'report/report_contract_template.xml',
        'report/report_contract_committee.xml',
        'report/report.xml',
        'report/report_contract_invoice_view.xml',
        'report/contract_single_xls_report.xml',
        'report/contract_single_doc_report.xml',
        'report/contract_to_expire_doc_report.xml',
        'report/contract_to_expire_xls_report.xml',

        'report/report_template_contract_committee.xml',
        'report/report_acta_contract_committee.xml',

        'report/report_contract_to_expire_percent.xml',
        'report/contract_single_doc_percent_report.xml',
        'report/contract_hiring_status_xls_report.xml',



    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    "post_init_hook": "post_init_hook",
}
