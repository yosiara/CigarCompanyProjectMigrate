# -*- coding: utf-8 -*-
{
    'name': 'ICT',
    'version': '18.1',
    'category': 'Inventory',
    'summary': 'ICT department management',
    'description': """
        Module to manage ICT:
        - Computers and their components
        - Domain users
        - Mobile phones and lines
        - ICT services
    """,
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'depends': ['base', 'web', 'mail', 'hr', 'maintenance'],
    'data': [
        "security/ir.model.access.csv",
        "views/ict_menus.xml",
        "views/ict_computer_views.xml",
        "views/ict_employee_views.xml",
        "views/ict_phone_views.xml",
        "views/ict_service_views.xml",
        "views/ict_dashboard.xml",
        # 'views/ict_reports_views.xml',
        "views/ict_computer_component_views.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'ict/static/src/components/advanced_search/*',
            'ict/static/src/components/assignment_timeline/*',
            'ict/static/src/components/dashboard/*',
            'ict/static/src/components/dynamic_form/*',
            'ict/static/src/components/live_stats/*',
            'ict/static/src/components/quick_create/*',
            'ict/static/src/views/computer_kanban/*',
            'ict/static/src/scss/computer_form.scss'
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}