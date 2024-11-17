# -*- coding: utf-8 -*-


from odoo import models, fields, api, tools, _


class EfficientReport(models.AbstractModel):
    _name = 'report.process_control.efficient_report'

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('process_control.efficient_report')
        docargs = {
            'doc_model': report.model,
            'data': {},
        }

        query = """SELECT
                    CAST("date" as VARCHAR) || CAST(productive_section as VARCHAR) || CAST(turn as VARCHAR) AS key,
                    date,
                    productive_section,
                    "public".process_control_interruption.productive_line_id as productive_line,
                    turn,
                    cause,
                    "public".process_control_interruption_type.name as interruption_name,
                    "public".process_control_interruption.productive_line_id as productive_line,
                    "public".process_control_machine.name as machine_name,
                    "public".process_control_machine_set_of_peaces."name" as set_of_peace,
                    frequency AS frequency,
                    "time" AS time,
                    interruption_type,
                    productive_capacity AS  productive_capacity,
                    plan_time AS plan_time,
                    production_in_proccess_control AS production_done,
                    productive_capacity
                FROM
                    "public".process_control_interruption
                INNER JOIN "public".process_control_tecnolog_control ON "public".process_control_interruption.tec_control_model = "public".process_control_tecnolog_control."id"
                INNER JOIN "public".process_control_interruption_type ON "public".process_control_interruption.interruption_type = "public".process_control_interruption_type."id"
                LEFT JOIN "public".process_control_machine ON "public".process_control_interruption.machine_id = "public".process_control_machine."id"
                LEFT JOIN "public".process_control_machine_set_of_peaces ON "public".process_control_interruption.set_of_peaces_id = "public".process_control_machine_set_of_peaces.id
                """

        turns_domain = [('date', '<=', data['date_end']), ('date', '>=', data['date_start'])]
        prod_section_id = False

        if data['turn'] and data['productive_section']:
            query += """WHERE productive_section= '%s' and "date" BETWEEN '%s' and '%s' and turn= '%s'"""
            query %= (data['productive_section'], data['date_start'], data['date_end'], data['turn'])
            docargs.update({'turn': self.env['resource.calendar'].search([('id', '=', data['turn'])], limit=1)})
            turns_domain.append(('turn_calendar_id', '=', data['turn']))
            turns_domain.append(('productive_section_id', '=', data['productive_section']))
            prod_section_id = str(data['productive_section']) if data['productive_section'] > 9 else '0'+str(data['productive_section'])
        else:
            if not data['turn'] and data['productive_section']:
                query += """WHERE productive_section= '%s' and "date" BETWEEN '%s' and '%s'"""
                query %= (data['productive_section'], data['date_start'], data['date_end'])
                turns_domain.append(('productive_section_id', '=', data['productive_section']))
                prod_section_id = str(data['productive_section']) if data['productive_section'] > 9 else '0'+str(data['productive_section'])
            elif not data['productive_section'] and data['turn']:
                query += """WHERE "date" BETWEEN '%s' and '%s' and turn= '%s'"""
                query %= (data['date_start'], data['date_end'], data['turn'])
                docargs.update({'turn': self.env['resource.calendar'].search([('id', '=', data['turn'])], limit=1)})
                turns_domain.append(('turn_calendar_id', '=', data['turn']))
            else:
                query += """WHERE "date" BETWEEN '%s' and '%s'"""
                query %= (data['date_start'], data['date_end'])

        query += ' ORDER BY "key", productive_section, "date", turn, cause DESC'

        turnos_trabajados = self.env['process_control.tecnolog_control'].search_count(turns_domain)

        self.env.cr.execute(query)
        records_query = self.env.cr.dictfetchall()

        sum_frequency_exogena = 0.00
        sum_time_exogena = 0.00
        sum_frequency_endo = 0.00
        sum_time_endo = 0.00
        sum_production_done = 0.00
        sum_plan_time = 0.00
        sum_time_total = 0.00
        key_before = -1
        productividad_real = 0.00
        productividad_operativa = 0.00
        sum_time_exogena_tmp = 0.00
        real_produccion_time = 0.00
        count_lines = 0
        for i in range(0, len(records_query)):

            if not records_query[i]['productive_line'] and not records_query[i]['cause'] == 'exogena':
                sum_time_total += records_query[i]['time']

            if not records_query[i]['productive_line']:
                count_lines_tmp = len(self.env['process_control.productive_section'].search([('id', '=', records_query[i]['productive_section'])]).productive_line_ids)

                sum_time_exogena += records_query[i]['time'] * count_lines_tmp if records_query[i]['cause'] == 'exogena' else 0.00
                sum_time_endo += records_query[i]['time'] if records_query[i]['cause'] == 'endogena' else 0.00
            else:

                sum_time_exogena += records_query[i]['time'] if records_query[i]['cause'] == 'exogena' else 0.00
                sum_time_endo += records_query[i]['time'] if records_query[i]['cause'] == 'endogena' else 0.00

            sum_frequency_exogena += records_query[i]['frequency'] if records_query[i]['cause'] == 'exogena' else 0.00
            sum_frequency_endo += records_query[i]['frequency'] if records_query[i]['cause'] == 'endogena' else 0.00
            if records_query[i]['key'] != key_before:
                count_lines = len(self.env['process_control.productive_section'].search([('id', '=', records_query[i]['productive_section'])]).productive_line_ids)
                sum_production_done += records_query[i]['production_done']
                sum_plan_time = (records_query[i]['plan_time'] * 60.0) + sum_plan_time
                #if records_query[i]['productive_capacity']:
                real_produccion_time += ((records_query[i]['production_done'] * 10000.0) / records_query[i]['productive_capacity']) / 60.0
                #else:
                #    raise ValueError(_("Division by zero not defined"))
                productividad_real += (records_query[i]['plan_time'] * 60.0) * records_query[i]['productive_capacity']
                if not records_query[i]['productive_line']:
                    sum_time_exogena_tmp = records_query[i]['time'] * count_lines_tmp if records_query[i]['cause'] == 'exogena' else 0.00
                else:
                    sum_time_exogena_tmp = records_query[i]['time'] if records_query[i]['cause'] == 'exogena' else 0.00
                key_before = records_query[i]['key']
            else:
                if not records_query[i]['productive_line']:
                    sum_time_exogena_tmp += records_query[i]['time'] * count_lines_tmp if records_query[i]['cause'] == 'exogena' else 0.00
                else:
                    sum_time_exogena_tmp += records_query[i]['time'] if records_query[i]['cause'] == 'exogena' else 0.00
                if i+1 < len(records_query):
                    if records_query[i]['key'] != records_query[i+1]['key']:
                        productividad_operativa += ((records_query[i]['plan_time'] * 60.0)-sum_time_exogena_tmp) * records_query[i]['productive_capacity']
                        sum_time_exogena_tmp = 0.00
                else:
                    productividad_operativa += ((records_query[i]['plan_time'] * 60.0)-sum_time_exogena_tmp) * records_query[i]['productive_capacity']

        docargs.update({
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'turnos_trabajados': turnos_trabajados,
            'records': records_query,
            'sum_frequency_exogena': sum_frequency_exogena,
            'sum_time_exogena': sum_time_exogena,
            'sum_frequency_endo': sum_frequency_endo,
            'sum_time_total': sum_time_total,
            'sum_time_endo': sum_time_endo,
            'sum_production_done': sum_production_done,
            'sum_plan_time': sum_plan_time,
            'productividad_real': productividad_real,
            'productividad_operativa': productividad_operativa,
            'real_produccion_time': real_produccion_time,
            'count_lines': count_lines,
            'model': self,
            'productive_section': self.env['process_control.productive_section'].search([('id', '=', prod_section_id)], limit=1) if prod_section_id else False,
        })

        return report_obj.render('process_control.efficient_report', docargs)
