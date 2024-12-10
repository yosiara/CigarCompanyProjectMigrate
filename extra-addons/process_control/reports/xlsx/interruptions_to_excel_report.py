# -*- coding: utf-8 -*-
from odoo import models,fields, api, tools, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import logging
_logger = logging.getLogger(__name__)

from io import BytesIO

try:
    import xlsxwriter
except ImportError:
    raise ImportError(_("Python Library Import Error."))
 

class InterruptionsToExcelReport(models.AbstractModel):
    _name = "report.process_control.interruptions_to_excel_report"
    _description = "Interruptions to excel report"

    @api.model
    def generate_xlsx_report(self, data, response):
        # Get data
        tecnolog_control_ids = self.env['process_control.tecnolog_control'].search([('date', '>=', data["start_date"]), ('date', '<=', data["end_date"])])
        if not tecnolog_control_ids: # Empty data
           _logger.warning('There is no data to display.')
           return

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        
        # Title
        title = f"Listado de Interrupciones desde {data['start_date']} hasta {data['end_date']}"

        # Formats
        title_format = workbook.add_format({'bold': 1, 'align': 'center', 'valign': 'vcenter', 'font_size': 18, 'italic': 1, 'font_color': '#873b0f', 'underline': 2})
        header_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter'})
        data_format = workbook.add_format({'bold': 0})
        cell_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        
        # Add worksheet
        worksheet = workbook.add_worksheet("Interrupciones")
        
        # Insert logo.
        worksheet.merge_range("A1:D3", '')
        worksheet.insert_image("A1", '/mnt/extra-addons/process_control/static/src/img/hoja_turei.jpg', {'x_scale': 1.5, 'y_scale': 1.7})
        
        # Write the title.
        worksheet.merge_range("E1:N3", title, title_format)

        # Options to use in the table.
        options = {
            #"style": "Table Style Light 11",
            'total_row': True,
            "columns": [ # Header
                {"header": "No", "header_format": header_format, "format": data_format},
                {"header": "Año", "header_format": header_format, "format": data_format},
                {"header": "Mes", "header_format": header_format, "format": data_format},
                {"header": "Día", "header_format": header_format, "format": data_format},
                {"header": "Turno", "header_format": header_format, "format": data_format},
                {"header": "Módulo", "header_format": header_format, "format": data_format},
                {"header": "Inicio", "header_format": header_format, "format": data_format},
                {"header": "Fin", "header_format": header_format, "format": data_format},
                {"header": "Línea", "header_format": header_format, "format": data_format},
                {"header": "Máquina", "header_format": header_format, "format": data_format},
                {"header": "Subconjunto", "header_format": header_format, "format": data_format},
                {"header": "Tipo de interrupción", "header_format": header_format, "format": data_format},
                {"header": "Exógena/Endógena", "header_format": header_format, "format": data_format},
                {"header": "Tiempo (horas)", "header_format": header_format, "format": data_format},
            ],
        }

        # Add a table to the worksheet.
        worksheet.add_table("A5:N6", options)

        # Variables Decalaration
        row = 6
        max_len = []

        # Initial definition of column widths
        for h in options['columns']:
            max_len.append(len(h['header']))
        
        # Write data
        for tc in tecnolog_control_ids:
            for i in tc.interruption_ids:
                worksheet.write(row, 0, row - 5, cell_format) # write(row, col, *args)
                worksheet.write(row, 1, tc.date.year, cell_format)
                worksheet.write(row, 2, tc.date.month, cell_format)
                worksheet.write(row, 3, tc.date.day, cell_format)
                worksheet.write(row, 4, tc.turn_id.name, cell_format)
                worksheet.write(row, 5, tc.productive_section_id.name, cell_format)
                worksheet.write(row, 6, i.start_date, cell_format)
                worksheet.write(row, 7, i.end_date, cell_format)
                worksheet.write(row, 8, i.productive_line_id.name if i.productive_line_id else '', cell_format)
                worksheet.write(row, 9, i.machine_id.name if i.machine_id else '', cell_format)
                worksheet.write(row, 10, i.set_of_peaces_id.name if i.set_of_peaces_id else '', cell_format)
                worksheet.write(row, 11, i.interruption_type_id.name, cell_format)
                worksheet.write(row, 12, i.interruption_type_id.cause, cell_format)
                worksheet.write(row, 13, tc.plan_time, cell_format)

                # To calculate minimum column width
                max_tmp = len(str(row - 5))
                if max_tmp > max_len[0]:
                    max_len[0] = max_tmp
                max_tmp = len(tc.turn_id.name)
                if max_tmp > max_len[4]:
                    max_len[4] = max_tmp
                max_tmp = len(tc.productive_section_id.name)
                if max_tmp > max_len[5]:
                    max_len[5] = max_tmp
                max_tmp = len(i.productive_line_id.name) if i.productive_line_id else 0
                if max_tmp > max_len[8]:
                    max_len[8] = max_tmp
                max_tmp = len(i.machine_id.name) if i.machine_id else 0
                if max_tmp > max_len[9]:
                    max_len[9] = max_tmp
                max_tmp = len(i.set_of_peaces_id.name) if i.set_of_peaces_id else 0
                if max_tmp > max_len[10]:
                    max_len[10] = max_tmp
                max_tmp = len(i.interruption_type_id.name)
                if max_tmp > max_len[11]:
                    max_len[11] = max_tmp
                max_tmp = len(i.interruption_type_id.cause)
                if max_tmp > max_len[12]:
                    max_len[12] = max_tmp

                row += 1 # next row

        # Set the columns widths.
        for col in range(len(max_len)):
            worksheet.set_column(col, col, max_len[col] + 4.3) # set_column(first_col, last_col, width, cell_format, options)

                # if interruption.time:
                #     if interruption.interruption_type.cause == 'exogena' and not interruption.productive_line_id:
                #         worksheet.write('L'+str(aux_row), round(interruption.time * 2 / 60.00,2), data_format)
                #     elif not interruption.productive_line_id:
                #         worksheet.write('L'+str(aux_row), round(interruption.time * 2 / 60.00,2), data_format)
                #     else:
                #         worksheet.write('L'+str(aux_row), round(interruption.time / 60.00,2), data_format)
                # else:
                #     worksheet.write('L'+str(aux_row), "", data_format)

                # if interruption.frequency:
                #     worksheet.write('M'+str(aux_row), interruption.frequency, data_format)
                # else:
                #     worksheet.write('M'+str(aux_row), "", data_format)

                # aux_row += 1

        # Freeing up resources
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()