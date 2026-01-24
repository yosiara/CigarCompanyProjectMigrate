# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Whatsapp Accounting',
    'category': 'WhatsApp',
    'description': """This module Integrates Accounting with WhatsApp""",
    'depends': ['account', 'whatsapp'],
    'data': [
        'data/whatsapp_template_data.xml',
    ],
    'license': 'LGPL-3',
    'auto_install': True
}
