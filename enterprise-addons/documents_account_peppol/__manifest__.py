{
    "name": "Documents - Import from Peppol",
    "version": "1.0",
    "category": "Productivity/Documents",
    "summary": "Documents from Peppol",
    "description": """
Bridge module between the Documents and Peppol apps.
It allows importing of received Peppol documents
within the Documents app.
    """,
    "author": "Odoo SA",
    "license": "LGPL-3",
    "depends": ["account_peppol", "documents"],
    "data": ["views/res_config_settings_views.xml"],
    "auto_install": True,
}
