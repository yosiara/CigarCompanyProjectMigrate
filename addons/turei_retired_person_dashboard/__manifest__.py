# -*- coding: utf-8 -*-
{
    'name': "Tablero Sistema de Gestión de Jubilados (v1.0)",

    'author': "Desoft Holguin",
    'version': "10.0.1.1.0",
    'depends': [
        'turei_retired_person'
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/retired_dashboard.xml',

    ],
    'qweb': [
        "static/src/xml/retired_dashboard.xml",
    ],
    'images': ["static/description/banner.gif"],
    'license': "AGPL-3",
    'installable': True,
    'application': True,
}
