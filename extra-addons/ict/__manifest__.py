# -*- coding: utf-8 -*-
{
    'name': 'ICT',
    'version': '18.1',
    'category': 'Inventory',
    'summary': 'Information and Communication Technologies',
    'description': """
        Module to manage ICT:
        - Domain users
        - Computers and their components
        - Mobile phones and lines
        - Fixed phones and extensions
        - ICT services
    """,
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'depends': ['mail', 'hr', 'maintenance'],
    'data': [
        'security/ict_security.xml',
        'security/ir.model.access.csv',
        'views/ict_menus_views.xml',
        'views/ict_computer_application_views.xml',
        'views/ict_computer_component_views.xml',
        'views/ict_computer_views.xml',
        'views/ict_dashboard_views.xml',
        'views/ict_employee_views.xml',
        'views/ict_phone_views.xml',
        'views/ict_mobile_views.xml',
        'views/ict_service_views.xml',
        'views/ict_mobile_line_views.xml',
        'views/ict_phone_extension_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            # Styles
            'ict/static/src/scss/form/common_form.scss',
            'ict/static/src/scss/form/computer_form.scss',
            'ict/static/src/scss/form/employee_form.scss',
            'ict/static/src/scss/form/mobile_form.scss',
            'ict/static/src/scss/form/mobile_line_form.scss',
            'ict/static/src/scss/form/phone_form.scss',
            'ict/static/src/scss/form/phone_extension_form.scss',
            'ict/static/src/scss/kanban/common_kanban.scss',
            'ict/static/src/scss/kanban/computer_kanban.scss',
            'ict/static/src/scss/kanban/employee_kanban.scss',
            'ict/static/src/scss/kanban/mobile_kanban.scss',
            # Components
            'ict/static/src/components/dashboard/*',
            'ict/static/src/components/employee_chat/*',
            'ict/static/src/components/status_badge/*',
            # Views
            'ict/static/src/views/kanban/computer_kanban/*',
            'ict/static/src/views/kanban/employee_kanban/*',
            'ict/static/src/views/kanban/mobile_kanban/*',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
