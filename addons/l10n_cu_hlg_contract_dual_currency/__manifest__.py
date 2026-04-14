# -*- coding: utf-8 -*-

{
    'name': 'Contract Dual Currency',
    'summary': '',
    'description': """

""",

    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",

    # Categories can be used to filter modules in modules listing.
    # Check /odoo/addons/base/module/module_data.xml for the full list.
    'category': 'Contract',
    'version': '1.0',
    # Any module necessary for this one to work correctly.
    'depends': ['l10n_cu_hlg_contract', 'l10n_cu_account_dual_currency'],

    # Always loaded.
    'data': [
        "views/contract_view.xml",

        "report/report.xml",
        "report/report_contract_invoice_view.xml",
        "report/report_contract_template.xml",
        "report/contract_single_doc_report_dual.xml",
        ],

    # Only loaded in demonstration mode.
    'demo': [
    ],
    'qweb': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

