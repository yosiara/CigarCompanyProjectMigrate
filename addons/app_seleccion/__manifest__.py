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
    'name': 'Selección de Personal',
    'description': 'Proceso de seleccion de personal',
    'author': 'Desoft Holguín',
    'summary': 'Aplicación para la Selección de Personal en Empresa de cigarros Lázaro Peña González',
    'description': "Aplicación para la Selección de Personal en Empresa de cigarros Lázaro Peña González",
    'website': "www.desoft.cu",
    'images': [],
    'depends': ['base','l10n_cu_base','inputmask_widget','hr_recruitment','l10n_cu_hlg_hr','l10n_cu_hlg_uforce','l10n_cu_report_docxtpl'],
    'application': True,
    'data': [

        # ..................Security.....................
        'security/app_seleccion_security.xml',
        'security/ir.model.access.csv',

        # Views...
        'views/candidato_view.xml',
        'views/seleccion_view.xml',

        #'views/curso_view.xml',


		# Wizards...

        'wizard/wzd_cmedico.xml',
        'wizard/wzd_atencion.xml',
		'wizard/wzd_breferenciap.xml',
        'wizard/wzd_rvsociolaboral.xml',
        'wizard/wzd_revalpsicologica.xml',
        'wizard/wzd_msrechazada.xml',
        'wizard/wzd_mintegracion.xml',
        'wizard/wzd_xls.xml',
        'wizard/wzd_xls_vcurso.xml',
        'wizard/wzd_xls_cyears.xml',
        'wizard/wzd_xls_cmes.xml',
        'wizard/wzd_mcomport_mes.xml',
        'wizard/wzd_mpetapas.xml',
        'wizard/wzd_mecurso.xml',
        'wizard/wzd_mcexperto.xml',
        'wizard/wzd_mcexpertoin.xml',
        'wizard/wzd_mpaprobados.xml',

		# Reports...
        'reports/layout.xml',
        #'reports/report_application.xml',
        'reports/print_cmedico_report.xml',
        'reports/print_atencion_report.xml',
        'reports/print_breferenciap_report.xml',
        'reports/print_rvsociolaboral_report.xml',
        'reports/print_revalpsicologica_report.xml',
        'reports/print_mcexperto_report.xml',
        'reports/print_mcexpertoin_report.xml',
        'reports/print_msrechazada_report.xml',
        'reports/print_mintegracion_report.xml',
        'reports/print_revaluacion_report.xml',
        'reports/xls_report.xml',
        'reports/xls_report_vcurso.xml',
        'reports/xls_report_cyears.xml',
        'reports/xls_report_cmes.xml',
        'reports/print_resumen_solicitud.xml',
        'reports/print_mcomport_mes_report.xml',
        'reports/print_mporetapas.xml',
        'reports/print_mecurso.xml',
        'reports/print_mpaprobados_report.xml',
        'reports/print_solicitud_experto.xml',
        'reports/print_solicitud_experto_reporte.xml',
        # Data
        'data/seleccion_data.xml',
        'data/seleccion_email_template_data.xml',
        'data/ir_cron_data.xml',

    ],
    'demo': [],
    'test': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'css': [],

}
