# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2012-2015 Odoo Desoft Solutions Suite (<http://odoo.hlg.desoft.cu>).
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
    'name' : 'Structure',
    'version' : '1.0',
    'author' : 'Desoft. Holguín. Cuba.',
    'website': "www.desoft.cu",
    'category' : 'base',
    'summary': 'Structure and locals',
    'description' : """
Structure and locals.
====================================
Allows defines the company's physical structure, floors and other zones.
""",    
    'depends' : ['l10n_cu_base','hr'],
    'data': [
        'security/l10n_cu_locals_security.xml', #Grupos de usuarios y reglas de seguridad
        'security/ir.model.access.csv', #Permisos de Control de acceso
        'views/l10n_cu_locals_view.xml', #Vistas y menues
        #'wizard/l10n_cu_locals_import_view.xml', #Vista asistente de importacion
        #'data/l10n_cu_locals_import_data.xml',
        ],
    'qweb' : [ ],
    'demo': [ 'demo/l10n_cu_locals_demo.xml'],
    'test': [ ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
