# -*- coding: utf-8 -*-
{
    'name': "Tablero Mentor v3.1",

    'author': "Desoft Holguin",
    'version': "10.0.1.1.0",
    'depends': [
        'l10n_cu_hlg_contract'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/contract_sale_dashboard_menu_view.xml',
        'views/sale_contract_dashboard.xml',
        'views/purchase_contract_dashboard.xml',

    ],
    'qweb': [
        "static/src/xml/hr_dashboard.xml",
        "static/src/xml/hr_dashboard_purchase.xml",

    ],
    'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
