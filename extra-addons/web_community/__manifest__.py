# -*- coding: utf-8 -*-

{
    'name': 'Web Community',
    'author': 'Computer Science Specialist, '
    'Yosiel R. Arango Arencibia. ',
    'category': 'Themes/Themes',
    'version': '1.0',
    'description': """
Odoo Community Web Client
===========================

This module modifies the web addon to provide Community design and responsiveness.
        """,
    'depends': ['web', 'base_setup'],
    'auto_install': ['web'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            ('after', 'web/static/src/scss/primary_variables.scss', 'web_community/static/src/**/*.variables.scss'),
            ('before', 'web/static/src/scss/primary_variables.scss', 'web_community/static/src/scss/primary_variables.scss'),
        ],
        'web._assets_secondary_variables': [
            ('before', 'web/static/src/scss/secondary_variables.scss', 'web_community/static/src/scss/secondary_variables.scss'),
        ],
        'web._assets_backend_helpers': [
            ('before', 'web/static/src/scss/bootstrap_overridden.scss', 'web_community/static/src/scss/bootstrap_overridden.scss'),
        ],
        'web.assets_frontend': [
            'web_community/static/src/webclient/home_menu/home_menu_background.scss', # used by login page
            'web_community/static/src/webclient/navbar/navbar.scss',
        ],
        'web.assets_backend': [
            'web_community/static/src/webclient/**/*.scss',
            'web_community/static/src/views/**/*.scss',

            'web_community/static/src/core/**/*',
            'web_community/static/src/webclient/**/*.js',
            'web_community/static/src/webclient/**/*.xml',
            'web_community/static/src/views/**/*.js',
            'web_community/static/src/views/**/*.xml',

            # Don't include dark mode files in light mode
            ('remove', 'web_community/static/src/**/*.dark.scss'),
        ],
        'web.assets_web': [
            ('replace', 'web/static/src/main.js', 'web_community/static/src/main.js'),
        ],
        # ========= Dark Mode =========
        "web.dark_mode_variables": [
            # web._assets_primary_variables
            ('before', 'web_community/static/src/scss/primary_variables.scss', 'web_community/static/src/scss/primary_variables.dark.scss'),
            ('before', 'web_community/static/src/**/*.variables.scss', 'web_community/static/src/**/*.variables.dark.scss'),
            # web._assets_secondary_variables
            ('before', 'web_community/static/src/scss/secondary_variables.scss', 'web_community/static/src/scss/secondary_variables.dark.scss'),
        ],
        "web.assets_web_dark": [
            ('include', 'web.dark_mode_variables'),
            # web._assets_backend_helpers
            ('before', 'web_community/static/src/scss/bootstrap_overridden.scss', 'web_community/static/src/scss/bootstrap_overridden.dark.scss'),
            ('after', 'web/static/lib/bootstrap/scss/_functions.scss', 'web_community/static/src/scss/bs_functions_overridden.dark.scss'),
            # assets_backend
            'web_community/static/src/**/*.dark.scss',
        ],
        'web.tests_assets': [
            'web_community/static/tests/*.js',
        ],
        'web.qunit_suite_tests': [
            'web_community/static/tests/views/**/*.js',
            'web_community/static/tests/webclient/**/*.js',
            ('remove', 'web_community/static/tests/webclient/action_manager_mobile_tests.js'),
        ],
        'web.qunit_mobile_suite_tests': [
            'web_community/static/tests/views/disable_patch.js',
            'web_community/static/tests/mobile/**/*.js',
            'web_community/static/tests/webclient/action_manager_mobile_tests.js',
        ],
    },
    'license': 'LGPL-3',
}
