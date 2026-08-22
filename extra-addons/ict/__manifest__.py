# -*- coding: utf-8 -*-
{
    'name': 'ICT',
    'version': '18.1',
    'category': 'Inventory',
    'summary': 'Information and Communication Technologies',
    'description': """
        Module to manage ICT:
        - Computers and their components
        - Domain users
        - Mobile phones and lines
        - ICT services
    """,
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'depends': ['mail', 'hr', 'maintenance'],
    'data': [
        'security/ict_security.xml',
        'security/ir.model.access.csv',
        'views/ict_menus.xml',
        'views/ict_computer_application_views.xml',
        'views/ict_computer_component_views.xml',
        'views/ict_computer_views.xml',
        'views/ict_dashboard.xml',
        'views/ict_employee_views.xml',
        'views/ict_phone_views.xml',
        'views/ict_service_views.xml',
        # "views/ict_reports_views.xml",
        'views/ict.mobile.line_views.xml',
        'views/ict_phone_extension.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Components
            'ict/static/src/components/advanced_search/*',
            'ict/static/src/components/assignment_timeline/*',
            'ict/static/src/components/dashboard/*',
            'ict/static/src/components/dynamic_form/*',
            'ict/static/src/components/live_stats/*',
            'ict/static/src/components/quick_create/*',
            'ict/static/src/components/employee_chat/*',
            'ict/static/src/components/status_badge/*',
            # Views
            'ict/static/src/views/kanban/common_kanban.scss',
            'ict/static/src/views/kanban/employee_kanban/*',
            'ict/static/src/views/kanban/computer_kanban/*',
            'ict/static/src/views/kanban/mobile_kanban/*',
            # Styles
            'ict/static/src/scss/form/common_form.scss',
            'ict/static/src/scss/form/computer_form.scss',
            'ict/static/src/scss/form/employee_form.scss',
            'ict/static/src/scss/form/mobile_form.scss',
            'ict/static/src/scss/form/mobile_line_form.scss',
            'ict/static/src/scss/kanban/*.scss',
            # Others
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
