# -*- coding: utf-8 -*-

{
    "name": "External Database Connector",
    "summary": "Used to make connections to external databases...",
    "description": """
External Database Connector.
============================
Used to make connections to external databases...
    """,
    "author": "Computer Science Specialist, "
    "Yosiel R. Arango Arencibia. ",
    "category": "Tools",
    "version": "17.0",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
    ],
    # Data files to load...
    "data": [
        "views/base_menu.xml",
        "views/external_db_source_view.xml",
        #"security/db_external_connector_security.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
}
