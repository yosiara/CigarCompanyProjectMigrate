# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Period',
    'version': '1.0',
    'summary': 'Period',
    'sequence': 30,
    'description': """
    Period
    Lapsus of time anual or monthly for report uses.
    """,
    'category': 'base',
    'website': 'http://www.desoft.cu',
    'author': "Desoft. Holguín. Cuba.",
    'images': [],
    'depends': [],
    'data': [
        'views/period_view.xml',
        'security/ir.model.access.csv',
        'demo/l10n_cu_period_demo.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
