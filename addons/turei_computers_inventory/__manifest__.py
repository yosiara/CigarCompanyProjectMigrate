# -*- coding: utf-8 -*-

{
    'name': u'Modificaciones Turei Informática',
    'summary': 'Modificaciones Turei Informática',
    'description': """
Modificaciones Turei Informática
""",
    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': [
        'l10n_cu_hlg_computers_inventory'
        ],

    # Always loaded.
    'data': [
        'security/ir.model.access.csv',
        'views/turei_computers_inventory_views.xml',
        'reports/work_order_report.xml',
        'reports/equipment_file_report.xml',
    ],

    'demo': [
    ],

    'test': [
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

