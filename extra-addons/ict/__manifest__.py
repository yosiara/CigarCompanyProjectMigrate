# -*- coding: utf-8 -*-
{
    'name': 'ICT Management',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'ICT department inventory management',
    'description': """
        Module to manage ICT inventory:
        - Computers and their components
        - Domain users
        - Mobile phones and lines
        - ICT services
    """,
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'depends': ['base', 'web', 'mail', 'hr'],
    'data': [
        "security/ir.model.access.csv",
        "views/ict_menus.xml",
        "views/ict_computer_views.xml",
        "views/ict_employee_views.xml",
        "views/ict_phone_views.xml",
        "views/ict_service_views.xml",
        "views/ict_dashboard.xml",
        # 'views/ict_reports_views.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'ict/static/src/components/**/*.js',
            'ict/static/src/components/**/*.xml',
            'ict/static/src/components/computer_kanban/computer_kanban.scss',
            ('before', 'web/static/src/views/kanban/kanban.variables.scss', 'ict/static/src/components/computer_kanban/kanban.variables.scss'),
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}