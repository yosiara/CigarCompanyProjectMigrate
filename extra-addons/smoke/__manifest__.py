# -*- coding: utf-8 -*-
{
    "name": "Smoke",
    "author": "Computer Science Specialist, "
    "Yosiel R. Arango Arencibia. ",
    "category": "Sales",
    "version": "17.0",
    "license": "LGPL-3",
    "sequence": 1,
    "summary": "Management of the smoking process, Lázaro Peña Cigar Factory. Holguín, Cuba",
    "description": """
Module in development to facilitate the management of the smoking process for workers 
at the Lázaro Peña Cigar Factory. Holguín, Cuba.
    """,
    "depends": [
        "base",
        "db_external_connector",
    ],
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
    "demo": [
        "demo/demo.xml",
    ],
    "installable": True,
    "application": True,
}
