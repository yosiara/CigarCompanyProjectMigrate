# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import models, fields, api, tools
from odoo.http import addons_manifest
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, relativedelta
from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
from odoo.tools.translate import _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class HrTureiSmokingResume(ReportXlsx):
    @api.model
    def generate_xlsx_report(self, workbook, data, lines):
        merge_format = workbook.add_format(
            {'bold': 1, 'top': 1, 'bottom': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format.set_text_wrap()
        merge_format_bottom = workbook.add_format(
            {'bold': 1, 'bottom': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_bottom.set_text_wrap()
        merge_format_top = workbook.add_format(
            {'bold': 1, 'top': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        merge_format_top.set_text_wrap()
        merge_format_no_border = workbook.add_format(
            {'bold': 1, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 10})
        merge_format_no_border.set_text_wrap()
        normal_format = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'left', 'valign': 'vcenter', 'font_size': 10})
        normal_format.set_text_wrap()
        normal_format_center = workbook.add_format(
            {'bold': 0, 'border': 0, 'align': 'center', 'valign': 'vcenter', 'font_size': 10})
        normal_format_center.set_text_wrap()

        worksheet = workbook.add_worksheet("Fuma Mes")
        worksheet.insert_image('A1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/logo-landscape.jpg',
                               {'x_offset': 2, 'y_offset': 2, 'x_scale': 2, 'y_scale': 2.5})

        worksheet.insert_image('G1', addons_manifest['hr_turei'][
            'addons_path'] + '/hr_turei/static/src/img/cert.png',
                               {'x_offset': 2, 'y_offset': 2, 'x_scale': 0.8, 'y_scale': 0.8})

        lines_date = fields.Date.from_string(lines.expedition_date)
        eval_date = fields.Date.from_string(lines.date)
        worksheet.merge_range('B3:G3', tools.ustr(
            u'Holguín, %s de %s de %s' % (lines_date.day, self._get_month_string(lines_date.month), lines_date.year)),
                              merge_format_no_border)
        worksheet.merge_range('B4:G4', tools.ustr(u'"Año 58 de la Revolución"'), merge_format_no_border)
        worksheet.merge_range('B6:G6', tools.ustr('Informe Resumen de la Fuma'), merge_format_no_border)

        worksheet.set_row(0, 65)
        worksheet.set_row(7, 25)
        worksheet.set_row(10, 25)
        worksheet.set_row(16, 25)
        worksheet.set_column('A1:A1', 6)
        worksheet.set_column('B1:B1', 25)
        worksheet.set_column('C1:C1', 8)
        worksheet.set_column('D1:D1', 8)
        worksheet.set_column('E1:E1', 5)
        worksheet.set_column('F1:F1', 16)
        worksheet.set_column('G1:G1', 7)
        worksheet.set_column('H1:H1', 15)
        worksheet.set_column('I1:I1', 7)
        worksheet.set_column('J1:J1', 21)
        worksheet.set_column('K1:K1', 21)

        worksheet.merge_range('B10:B11', 'CONCEPTO', merge_format)
        worksheet.merge_range('C10:H10', 'TIPOS CIGARRILLOS', merge_format_top)
        worksheet.merge_range('C11:E11', 'CIGARROS CORTOS RUBIOS', merge_format_bottom)
        worksheet.merge_range('F11:G11', 'CIGARROS NEGROS CORTOS CRIOLLO', merge_format_bottom)
        worksheet.write('H11', 'Total', merge_format_bottom)
        worksheet.write('B12', 'CARTAS DE SOLICITUD', merge_format_no_border)
        worksheet.write('B13', 'FUMA DIARIA', merge_format_no_border)
        worksheet.write('B14', 'VENTAS TRABAJADOR', merge_format_no_border)
        worksheet.write('B15', 'Total', merge_format)

        worksheet.merge_range('B17:C17', 'Cartas de Solicitud Recibidas', merge_format)
        worksheet.write('D17', u'Dia/Mes', merge_format)
        worksheet.merge_range('E17:F17', 'CIGARROS CORTOS RUBIOS', merge_format)
        worksheet.merge_range('G17:H17', 'CIGARROS NEGROS CORTOS CRIOLLO', merge_format)

        info = self.get_data(lines)

        total_blond = info['info']['CARTAS DE SOLICITUD']['CIGARROS CORTOS RUBIOS']
        total_blond += info['info']['FUMA DIARIA']['CIGARROS CORTOS RUBIOS']
        total_blond += info['info']['VENTAS TRABAJADOR']['CIGARROS CORTOS RUBIOS']

        total_black = info['info']['CARTAS DE SOLICITUD']['CIGARROS NEGROS CORTOS CRIOLLO']
        total_black += info['info']['FUMA DIARIA']['CIGARROS NEGROS CORTOS CRIOLLO']
        total_black += info['info']['VENTAS TRABAJADOR']['CIGARROS NEGROS CORTOS CRIOLLO']

        worksheet.merge_range('B8:H8', tools.ustr(
            u'En el mes de %s se extrajeron del almacén de víveres %s cajetillas, de ellas %s cajetillas de criollos y %s cajetillas de aromas, desglosados en los siguientes conceptos:' % (
            self._get_month_string(eval_date.month), int(total_blond + total_black), int(total_black), int(total_blond))), normal_format)

        worksheet.merge_range('C12:E12', int(info['info']['CARTAS DE SOLICITUD']['CIGARROS CORTOS RUBIOS']),
                              normal_format_center)
        worksheet.merge_range('F12:G12', int(info['info']['CARTAS DE SOLICITUD']['CIGARROS NEGROS CORTOS CRIOLLO']),
                              normal_format_center)
        worksheet.write('H12', str(int(
            info['info']['CARTAS DE SOLICITUD']['CIGARROS CORTOS RUBIOS'] + info['info']['CARTAS DE SOLICITUD'][
                'CIGARROS NEGROS CORTOS CRIOLLO'])), normal_format_center)

        worksheet.merge_range('C13:E13', int(info['info']['FUMA DIARIA']['CIGARROS CORTOS RUBIOS']),
                              normal_format_center)
        worksheet.merge_range('F13:G13', int(info['info']['FUMA DIARIA']['CIGARROS NEGROS CORTOS CRIOLLO']),
                              normal_format_center)
        worksheet.write('H13', int(info['info']['FUMA DIARIA']['CIGARROS CORTOS RUBIOS'] + info['info']['FUMA DIARIA'][
            'CIGARROS NEGROS CORTOS CRIOLLO']), normal_format_center)

        worksheet.merge_range('C14:E14', int(info['info']['VENTAS TRABAJADOR']['CIGARROS CORTOS RUBIOS']),
                              normal_format_center)
        worksheet.merge_range('F14:G14', int(info['info']['VENTAS TRABAJADOR']['CIGARROS NEGROS CORTOS CRIOLLO']),
                              normal_format_center)
        worksheet.write('H14', int(
            info['info']['VENTAS TRABAJADOR']['CIGARROS CORTOS RUBIOS'] + info['info']['VENTAS TRABAJADOR'][
                'CIGARROS NEGROS CORTOS CRIOLLO']), normal_format_center)

        worksheet.merge_range('C15:E15', str(int(total_blond)), merge_format)
        worksheet.merge_range('F15:G15', str(int(total_black)), merge_format)
        worksheet.write('H15', str(int(total_blond + total_black)), merge_format)

        i = 17
        total_blond = total_black = 0
        for letter in info['list']:
            date = datetime.strptime(letter['date'], DEFAULT_SERVER_DATETIME_FORMAT).strftime('%d/%m')
            worksheet.merge_range(i, 1, i, 2, tools.ustr(letter['description']), normal_format)
            worksheet.write(i, 3, date, normal_format)
            if letter['type'] == 'CIGARROS CORTOS RUBIOS':
                total_blond += letter['amount']
                worksheet.merge_range(i, 4, i, 5, int(letter['amount']), normal_format_center)
                worksheet.merge_range(i, 6, i, 7, '', normal_format_center)
                worksheet.merge_range(i, 8, i, 9, '', normal_format_center)
                worksheet.write(i, 10, '', normal_format_center)
            if letter['type'] == 'CIGARROS NEGROS CORTOS CRIOLLO':
                total_black += letter['amount']
                worksheet.merge_range(i, 4, i, 5, '', normal_format_center)
                worksheet.merge_range(i, 6, i, 7, int(letter['amount']), normal_format_center)
                worksheet.merge_range(i, 8, i, 9, '', normal_format_center)
                worksheet.write(i, 10, '', normal_format_center)

            i += 1

        worksheet.merge_range(i, 1, i, 3, tools.ustr('Total'), merge_format)
        worksheet.merge_range(i, 4, i, 5, int(total_blond), merge_format)
        worksheet.merge_range(i, 6, i, 7, int(total_black), merge_format)

    def get_data(self, lines):
        start = datetime.strptime(lines.date, DEFAULT_SERVER_DATE_FORMAT)
        temp = datetime(start.year, start.month, 28) + timedelta(days=4)
        start = datetime(start.year, start.month, 1).strftime(DEFAULT_SERVER_DATE_FORMAT)
        end = (temp - timedelta(days=temp.day)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        sql = """
                SELECT     TOP 100 PERCENT inv_documento.numero, inv_documento.fecha, gen_producto.descripcion, inv_movimiento.cantidad, 
                              inv_documento.descripcion AS COMENTARIO, CASE WHEN (dbo.inv_documento.descripcion LIKE '%%fuma Diaria%%') OR
                              (dbo.inv_documento.descripcion LIKE '%%Fuma Interna%%') OR
                              (dbo.inv_documento.descripcion LIKE '%%INTERNA%%') OR
                              (dbo.inv_documento.descripcion LIKE '%%Fuma finca%%') OR
                              (dbo.inv_documento.descripcion LIKE '%%FINCA%%') 
                              THEN 'FUMA DIARIA' WHEN dbo.inv_documento.descripcion LIKE '%%IPV%%' THEN 'VENTAS TRABAJADOR' ELSE 'CARTAS DE SOLICITUD' END AS TIPO
                FROM         inv_documento INNER JOIN
                                      inv_documentogasto ON inv_documento.iddocumento = inv_documentogasto.iddocumento INNER JOIN
                                      cos_centro ON inv_documentogasto.idcentro = cos_centro.idcentro INNER JOIN
                                      inv_movimiento ON inv_documento.iddocumento = inv_movimiento.iddocumento INNER JOIN
                                      gen_producto ON inv_movimiento.idproducto = gen_producto.idproducto
                WHERE     (cos_centro.clave = '3041') AND (inv_documento.fecha >= '%s') AND (inv_documento.fecha <= '%s')
                ORDER BY inv_documento.fecha, TIPO
        """ % (start, end)

        try:
            connection = lines.connection_id.connect()
            cursor = connection.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            requests_letter = []
            info = {
                'CARTAS DE SOLICITUD': {'CIGARROS CORTOS RUBIOS': 0, 'CIGARROS NEGROS CORTOS CRIOLLO': 0},
                'FUMA DIARIA': {'CIGARROS CORTOS RUBIOS': 0, 'CIGARROS NEGROS CORTOS CRIOLLO': 0},
                'VENTAS TRABAJADOR': {'CIGARROS CORTOS RUBIOS': 0, 'CIGARROS NEGROS CORTOS CRIOLLO': 0},
            }
            for row in rows:
                if row[5] == 'CARTAS DE SOLICITUD':
                    requests_letter.append(
                        {'date': tools.ustr(row[1]), 'type': tools.ustr(row[2]), 'description': tools.ustr(row[4]),
                         'amount': int(row[3])})
                    if tools.ustr(row[2]) == u'CIGARROS CORTOS RUBIOS':
                        info['CARTAS DE SOLICITUD']['CIGARROS CORTOS RUBIOS'] += row[3]
                    elif tools.ustr(row[2]) == u'CIGARROS NEGROS CORTOS CRIOLLO':
                        info['CARTAS DE SOLICITUD']['CIGARROS NEGROS CORTOS CRIOLLO'] += row[3]
                elif row[5] == 'FUMA DIARIA':
                    if tools.ustr(row[2]) == u'CIGARROS CORTOS RUBIOS':
                        info['FUMA DIARIA']['CIGARROS CORTOS RUBIOS'] += row[3]
                    elif tools.ustr(row[2]) == u'CIGARROS NEGROS CORTOS CRIOLLO':
                        info['FUMA DIARIA']['CIGARROS NEGROS CORTOS CRIOLLO'] += row[3]
                elif row[5] == 'VENTAS TRABAJADOR':
                    if tools.ustr(row[2]) == u'CIGARROS CORTOS RUBIOS':
                        info['VENTAS TRABAJADOR']['CIGARROS CORTOS RUBIOS'] += row[3]
                    elif tools.ustr(row[2]) == u'CIGARROS NEGROS CORTOS CRIOLLO':
                        info['VENTAS TRABAJADOR']['CIGARROS NEGROS CORTOS CRIOLLO'] += row[3]

            return {
                'list': requests_letter,
                'info': info
            }
            cursor.close()
            connection.close()
        except Exception as e:
            connection.close()
            raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                 the Database and make sure to select the correct one..."""))

    def _get_month_string(self, month):
        if month == 1:
            return _('January')
        elif month == 2:
            return _('February')
        elif month == 3:
            return _('March')
        elif month == 4:
            return _('April')
        elif month == 5:
            return _('May')
        elif month == 6:
            return _('June')
        elif month == 7:
            return _('July')
        elif month == 8:
            return _('August')
        elif month == 9:
            return _('September')
        elif month == 10:
            return _('October')
        elif month == 11:
            return _('November')
        elif month == 12:
            return _('December')


HrTureiSmokingResume('report.hr_turei.smoking_resume', 'hr_turei.smoking_resume_wzd')
