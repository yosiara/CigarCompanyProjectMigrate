# -*- coding: utf-8 -*-
{
    'name': 'IT Management',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'IT department inventory management',
    'description': """
        Module to manage IT inventory:
        - Computers and their components
        - Domain users
        - Mobile phones and lines
        - IT services
    """,
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'depends': ['base', 'web', 'mail', 'hr'],
    'data': [
        "security/ir.model.access.csv",
        "views/it_menus.xml",
        "views/it_computer_views.xml",
        "views/it_employee_views.xml",
        "views/it_phone_views.xml",
        "views/it_service_views.xml",
        "views/it_dashboard.xml",
        # 'views/it_reports_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'it/static/src/components/**/*.js',
            'it/static/src/components/**/*.xml',
            'it/static/src/components/computer_kanban/computer_kanban.scss',
            ('before', 'web/static/src/views/kanban/kanban.variables.scss', 'it/static/src/components/computer_kanban/kanban.variables.scss'),
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}