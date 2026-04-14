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
    'name': u'Turei Recursos Humanos',
    'version': '0.9',
    'author': u'Desoft. Holguín. Cuba.',
    'category': 'hr',
    'sequence': 20,

    'summary': u'Personalizacion de Recursos Humano para la Empresa de cigarrillos "Lázaro Peña".',
    'description': """
         Personalizacion de Recursos Humano para la Empresa de cigarrillos "Lázaro Peña".
        """,
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['turei_resource_calendar', 'report_xlsx'],
    'data': [
        'security/hr_turei_security.xml',
        'security/ir.model.access.csv',
        'data/hr_turei_data.xml',
        'views/hr_turei_view.xml',
        'views/hr_turei_external_staff_view.xml',
        'views/hr_smokes_view.xml',
        'views/hr_turei_daily_smoking_view.xml',
        'views/hr_turei_attendance_view.xml',
        'views/hr_turei_employee_movement.xml',
        'wizard/hr_turei_daily_smoking_list_wzd.xml',
        'wizard/hr_turei_daily_smoking_pickup_list_wzd.xml',
        'wizard/hr_turei_daily_smoking_delivery_list_wzd.xml',
        'wizard/hr_turei_weekly_smoking_delivery_list_wzd.xml',
        'wizard/hr_turei_smoking_additional_incidences_wzd.xml',
        'wizard/hr_turei_create_employee_movements_wzd.xml',
        'wizard/hr_turei_set_employee_turn_wzd.xml',
        'wizard/hr_turei_te_overcompliance_wzd.xml',
        'wizard/hr_turei_smoking_resume_wzd.xml',
        'report/hr_turei_daily_smoking_list.xml',
        'report/hr_turei_daily_smoking_pickup_list.xml',
        'report/hr_turei_daily_smoking_delivery_list.xml',
        'report/hr_turei_weekly_smoking_delivery_list.xml',
        'report/hr_turei_smoking_resume.xml'
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
