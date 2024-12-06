# -*- coding: utf-8 -*-
{
    "name": "Smoke",
    "summary": "Management of the smoking process, Lázaro Peña Cigar Factory. Holguín, Cuba",
    "description": """
        Module in development to facilitate the management of the smoking process for workers 
        at the Lázaro Peña Cigar Factory. Holguín, Cuba.
    """,
    "author": "Yosiel Arango Arencibia",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Turei",
    "version": "17.0",
    "license": "LGPL-3",
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
        "views/base_menu.xml",
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
}
