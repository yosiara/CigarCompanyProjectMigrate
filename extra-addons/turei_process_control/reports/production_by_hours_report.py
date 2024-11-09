# -*- coding: utf-8 -*-


from odoo import models, api


class ReportProductionByHours(models.AbstractModel):
    _name = 'report.turei_process_control.production_by_hours_report'

    def process_query(self, data):
        query = """SELECT
                attendance_id,
                hour_production,
                (SELECT "name" from turei_process_control_productive_section where "id" = productive_section),
                productive_section,
                AVG(production_count)
            FROM
                turei_process_control_production_by_hours
            INNER JOIN turei_process_control_tecnolog_control_model ON (
                tecnolog_control_id = turei_process_control_tecnolog_control_model."id"
            )
            WHERE turei_process_control_tecnolog_control_model."date" BETWEEN '%s' and '%s'
        """ % (data['date_start'], data['date_end'])

        conditions = []
        if 'turn' in data and data['turn']:
            conditions.append('turn = %d' % data['turn'])
        if 'productive_section' in data and data['productive_section']:
            conditions.append('productive_section = %d' % data['productive_section'])

        if len(conditions) > 0:
            query += ' AND ' + conditions[0]
            if len(conditions) > 1:
                query += ' AND ' + conditions[1]
        query += ' GROUP BY turn, productive_section, hour_production, attendance_id, name ORDER BY attendance_id, turn, hour_production, name, productive_section'

        self._cr.execute(query)
        return self.sort_data(self._cr.dictfetchall())

    def sort_data(self, records):
        # res debera ser igual a {'hora1':
        # {'productive_section1': avg de la production, 'productive_section2': avg de la production}}
        res = {'x': [], 'y': [], 'production_hours': [], 'productive_sections': [], 'matrix': None}
        matrix = []
        for re in records:
            if re['hour_production'] not in res['x']:
                res['x'].append(re['hour_production'])
            if re['productive_section'] not in res['y']:
                res['y'].append(re['productive_section'])
                res['productive_sections'].append(re['name'])

        for i in range(len(res['y'])-1):
            for j in range(i+1, len(res['y'])):
                if res['productive_sections'][i] > res['productive_sections'][j]:
                    aux = res['y'][i]
                    res['y'][i] = res['y'][j]
                    res['y'][j] = aux

                    aux_p = res['productive_sections'][i]
                    res['productive_sections'][i] = res['productive_sections'][j]
                    res['productive_sections'][j] = aux_p

        for x in range(len(res['x'])):
            matrix.append([])
            for y in range(len(res['y'])):
                matrix[x].append(0)

        for re in records:
            index_x = res['x'].index(re['hour_production'])
            index_y = res['y'].index(re['productive_section'])
            matrix[index_x][index_y] += round(re['avg'], 3)

        res['matrix'] = matrix
        return res

    @api.model
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('turei_process_control.production_by_hours_report')
        records = self.process_query(data)
        docargs = {
            'doc_model': report.model,
            'docs': records,
            'date_start': data['date_start'],
            'date_end': data['date_end'],
            'turn': self.env['resource.calendar'].browse([data['turn']]).sgp_turn_id.sgp_id,
            'max_len': len(records['productive_sections']),
            'productive_sections': records['productive_sections']
        }
        return report_obj.render('turei_process_control.production_by_hours_report', docargs)
