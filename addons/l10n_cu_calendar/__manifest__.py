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
    'name': 'Agenda Express v3.0.0',
    'version': '3.0',
    'author': u'Desoft. Holguín. Cuba.',
    'category': 'hr',
    'sequence': 20,

    'summary': u'Sistema de planificación del trabajo.',
    'description': """
         Sistema para gestionar la planificación de las actividades laborales (plan de trabajo) en las empresas cubanas. Genera los planes de trabajo según los modelos establecidos en la Instrucción 1/2012.
        """,
    'website': 'http://www.desoft.cu',
    'images': [],
    'depends': ['l10n_cu_period', 'l10n_cu_locals', 'calendar', 'l10n_cu_hlg_hr', 'l10n_cu_report_docxtpl'],
    'data': [
        'security/l10n_cu_calendar_security.xml',
        'security/ir.model.access.csv',
        'wizard/l10n_cu_calendar_print_individual_plan_view.xml',
        'wizard/l10n_cu_calendar_print_group_plan_view.xml',
        # 'wizard/l10n_cu_calendar_print_anual_group_plan_view.xml',
        'views/l10n_cu_calendar_view.xml',
        'views/hr_view.xml',
        'views/res_partner_view.xml',
        'views/res_company_view.xml',
        'views/res_config_view.xml',
        'views/l10n_cu_calendar_templates.xml',
        'wizard/l10n_cu_calendar_actualizar_partner_employee_view.xml',
        'wizard/l10n_cu_calendar_registry_information_view.xml',
        'wizard/l10n_cu_calendar_registry_information_view.xml',
        'wizard/l10n_cu_calendar_to_next_year_view.xml',
        'wizard/l10n_cu_calendar_attendee_done_all_wzd.xml',
        'wizard/l10n_cu_calendar_attendee_not_done_all_wzd.xml',
        'wizard/l10n_cu_calendar_group_add_employee_view.xml',
        # 'reports/df_agenda_individual_plan_view.xml',
        # 'reports/df_agenda_group_plan_view.xml',
        'reports/l10n_cu_calendar_reports.xml',
        'reports/l10n_cu_calendar_individual_plan_report.xml',
        'reports/l10n_cu_calendar_individual_plan_one_page_report.xml',
        'reports/l10n_cu_calendar_group_plan_report.xml',
        'reports/l10n_cu_calendar_anual_group_plan_report.xml',
        'reports/l10n_cu_calendar_individual_plan_resumen_report.xml',
        'reports/l10n_cu_calendar_group_report.xml',
        'reports/l10n_cu_calendar_group_plan_resumen_report.xml',
        'reports/l10n_cu_calendar_detail_report.xml',
        'reports/l10n_cu_calendar_detail_no_categ_report.xml',
        'reports/l10n_cu_calendar_group_plan_category_report.xml',
        # 'reports/df_agenda_group_report.xml',

        'data/l10n_cu_calendar_data.xml',

        # Reporte relacionado con la comprobacion de coincidencias en tiempo de las tareas de los partners
        # 'wizard/l10n_cu_calendar_comprobacion_coincidencia_view.xml',
        # 'reports/l10n_cu_calendar_comprobacion_coincidencia_doc_report.xml',

    ],
    'demo': [
        # 'demo/l10n_cu_calendar_demo.xml'
    ],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],
    "post_init_hook": "post_init_hook",
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
