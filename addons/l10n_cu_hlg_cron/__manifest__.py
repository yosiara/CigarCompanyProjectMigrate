# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Cron',
    'version' : '1.0',
    'summary': 'Update cron',
    'sequence': 30,
    'description': """
        Update cron
    """,
    'category': 'Tools',
    'website': 'http://www.desoft.cu',
    'author': "Desoft. Holguín. Cuba.",
    'images' : [],
    'depends' : ['l10n_cu_base','l10n_cu_hlg_db_external_connector'],
    'data': [
        'views/ir_cron_inherit_view.xml',
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
