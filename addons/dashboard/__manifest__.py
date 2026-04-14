{
    "name": "Dashboard Maintenance",
    "version": "1.0",
    "depends": [
        'base',
        'maintenance'
    ],
    "category": "Dashboard",
    "data": [
        "data/dashboard_data.xml",
        "security/dashboard_security.xml",
        "security/ir.model.access.csv",
        "views/dashboard_view.xml",
        "views/res_config_view.xml",
        "views/assets.xml",
    ],
    'installable': True,
    'images': ['static/description/logo.png']
}
