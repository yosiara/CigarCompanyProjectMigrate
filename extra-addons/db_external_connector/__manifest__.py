# -*- coding: utf-8 -*-

{
    "name": "DB External Connector",
    "summary": "Used to make connections to external databases...",
    "description": """
DB External Connector
======================

Used to make connections to external databases...
    """,
    "author": "Computer Science Specialist, "
    "Yosiel R. Arango Arencibia. ",
    "category": "Tools",
    "version": "17.0",
    "license": "LGPL-3",
    "depends": ["mail"],
    # Data files to load...
    "data": [
        # Security
        "security/db_external_connector_security.xml",
        "security/ir.model.access.csv",
        
        # Views
        "views/base_menu.xml",
        "views/external_db_source_view.xml",
    ],
    "installable": True,
}
