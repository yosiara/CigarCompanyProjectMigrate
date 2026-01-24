{
    'name': "POS Avatax",
    'summary': "Add Avatax support to POS",
    'description': "This module adds Avatax support to POS.",
    'version': "1.0",
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'account_avatax'],
    'auto_install': ['point_of_sale', 'account_avatax'],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_avatax/static/src/**/*',
        ],
    },
}
