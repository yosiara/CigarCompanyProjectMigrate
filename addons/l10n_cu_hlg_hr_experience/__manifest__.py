# -*- coding: utf-8 -*-

{
    "name": "Experience Management",
    "version": "10.0.1.0.0",
    'author': 'Desoft. Holguín. Cuba.',
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr"],
    "data": [
        "data/hr_experience_data.xml",
        "security/ir.model.access.csv",
        #"security/hr_security.xml",
        "views/hr_employee_view.xml",
        "views/hr_academic_view.xml",
        "views/hr_professional_view.xml",
        "views/hr_certification_view.xml",
        "views/hr_teacher_view.xml",
        "views/hr_science_view.xml",
        "views/hr_profession_view.xml",
    ],
    'installable': True
}
