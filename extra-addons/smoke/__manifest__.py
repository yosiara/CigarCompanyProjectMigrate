# -*- coding: utf-8 -*-
{
    "name": "Smoke",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "description": """
Long description of module's purpose
    """,
    "author": "Yosiel Arango Arencibia",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "db_external_connector",
    ],
    # always loaded
    "data": [
        # data
        "data/cron.xml",
        # security
        "security/ir.model.access.csv",
        # views
        "views/smoke.xml",
        "views/concept.xml",
        # reports
        "report/smoke_actions.xml",
        "report/smoke_templates.xml",
        # wizard
        "wizard/smoke_wzd.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
    "sequence": 1,
    "application": True,
    "web": {
        "images": {
            "logo": "/smoke/static/src/img/fumar-seeklogo.eps",
        }
    },
}
