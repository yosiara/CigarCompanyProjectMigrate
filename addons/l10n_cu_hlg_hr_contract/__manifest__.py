# -*- encoding: utf-8 -*-


{
    'name': 'Cuban Human Resource Contract ',
    'category': 'Human Resources',
    'author': 'Desoft. Holguín. Cuba.',
    'website': 'http://www.openerp.com',
    'depends': ['hr_contract', 'l10n_cu_hlg_hr', 'l10n_cu_hlg_hr_family', 'l10n_cu_hlg_hr_experience',
                'l10n_cu_hlg_hr_defense_inf'],  
    'version': '1.0',
    'active': False,
    'data': [
        'data/hr_contract_type_data.xml',
        'data/hr_contract_forma_pago_data.xml',
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_contract_config_view.xml',
        'views/hr_contract_menu_view.xml',
        'report/employee_register_report.xml',
        'report/l10n_cu_hlg_hr_contract_models_view.xml',
        'report/l10n_cu_hlg_hr_contract_models.xml',
        'wizard/wizard_view.xml',
        'wizard/report_authorized_signature_view.xml',
        'wizard/registry_view.xml',
    ],
    # 'css': ['static/src/css/my_css.css'],
    'test': [

    ],

    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
