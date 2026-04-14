# -*- coding:utf-8 -*-

{
    'name': 'Employee Family Information',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'Desoft. Holguín. Cuba.',
    'website': 'https://odoo-community.org/',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_family.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
}
