# -*- coding: utf-8 -*-
{
    'name': "uForce Dashboard (v1.0)",

    'author': "Desoft Holguin",
    'version': "10.0.1.1.0",
    'depends': [
        'l10n_cu_hlg_uforce'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/uforce_dashboard.xml',

    ],
    'qweb': [
        "static/src/xml/uforce_dashboard.xml",
    ],
    'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
