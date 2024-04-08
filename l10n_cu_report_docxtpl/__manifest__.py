# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Docx Report Engine',
    'summary': 'Reporting engine based on Libreoffice (DOCX -> DOCX, '
               'DOCX -> PDF, DOCX -> DOC, DOCX -> ODT, DOCX -> ODS, etc.)',
    'version': '10.0.2.0.0',
    'category': 'Reporting',
    'license': 'AGPL-3',
    'author': 'Desoft, Holguin',
    'website': 'http://www.desoft.cu',
    'depends': ['report'],
    'external_dependencies': {
        'python': ['docx','docxtpl']
    },
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/docxtpl_template.xml',
        'views/ir_report.xml',
        'views/report_docxtpl.xml',
    ],
    'installable': True,
}
