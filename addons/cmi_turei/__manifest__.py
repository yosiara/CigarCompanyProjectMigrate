# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Personalizacion Cuadro de mando integral Turei',
    'version': '0.9',
    'author': u'Desoft. Holguín. Cuba.',
    'category': 'hr',
    'sequence': 20,

    'summary': u'Module for control the main indicators of the enterprise.',
    'description': """
         Module for control the main indicators of the enterprise.
        """,
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['cmi', 'turei_web_login', 'turei_backend_theme'],
    'data': [
        'security/cmi_security.xml',
        'security/ir.model.access.csv',
        'views/cmi_view.xml',
        'data/cmi_turei_data.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
    # "post_init_hook": "post_init_hook",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
