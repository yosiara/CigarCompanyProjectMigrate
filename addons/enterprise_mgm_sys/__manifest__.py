# -*- coding: utf-8 -*-

{
    'name': u'Enterprise Management System',
    'summary': 'Enterprise Management System',
    'description': """
Enterprise Management System
""",
    'author': "Desoft. Holguín. Cuba.",
    'website': "www.desoft.cu",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': ['l10n_cu_hlg_hr', 'cmi', 'report_xlsx', 'l10n_cu_report_docxtpl', 'survey'],

    # Always loaded.
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/process.xml',
        'views/efficacy.xml',
        'views/registry.xml',
        'views/internal_agreement.xml',
        'views/risks.xml',
        'views/dashboard.xml',
        'views/quality.xml',
        'views/cmi.xml',
        'views/templates.xml',
        'wizard/registry_r1_wzd.xml',
        'wizard/internal_agreement_eval_wzd.xml',
        'reports/registry_r1.xml',
        'reports/registry_r1_resume.xml',
        'reports/risks_prevention_plan.xml',
        'reports/behavior_prevention_plan.xml',
        'reports/control_measures_efficacy.xml',
        'reports/control_compliance_measures.xml',
        'reports/improvement_program.xml',
        'reports/reports.xml',
        'data/mail_templates.xml',
        'data/data.xml',
    ],

    'demo': [
    ],

    'test': [
    ],

    'qweb': [
        "static/src/xml/dashboard.xml"
    ],

    'installable': True,
    'application': True,
    'auto_install': False,
}

