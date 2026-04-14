# -*- coding: utf-8 -*-


from odoo import models, fields, tools
from datetime import datetime, date


class InternalAgreementEvalWzd(models.TransientModel):
    _name = 'enterprise_mgm_sys.internal_agreement_eval_wzd'

    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    month = fields.Selection(string="Month",
                             selection=[('01', 'January'), ('02', 'February'), ('03', 'March'),
                                        ('04', 'April'),
                                        ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'),
                                        ('09', 'September'), ('10', 'October'), ('11', 'November'),
                                        ('12', 'December')], default=lambda month: '%02d' % datetime.today().month, required=True)

    def _get_month(self):
        if self.month == '01':
            return 'eval_ene'
        elif self.month == '02':
            return 'eval_feb'
        elif self.month == '03':
            return 'eval_mar'
        elif self.month == '04':
            return 'eval_apr'
        elif self.month == '05':
            return 'eval_may'
        elif self.month == '06':
            return 'eval_jun'
        elif self.month == '07':
            return 'eval_jul'
        elif self.month == '08':
            return 'eval_aug'
        elif self.month == '09':
            return 'eval_sept'
        elif self.month == '10':
            return 'eval_oct'
        elif self.month == '11':
            return 'eval_nov'
        elif self.month == '12':
            return 'eval_dec'

    def export_to_docx(self):
        areas = {}
        totals = {'G': 0, 'B': 0, 'R': 0, 'NA': 0, 'T': 0, 'TE': 0}
        evals = self.env['enterprise_mgm_sys.internal_agreement_eval'].search([('year', '=', self.year)])
        month = self._get_month()
        for e in evals:
            if e.source_area.id not in areas:
                areas[e.source_area.id] = {'name': e.source_area.name, 'G': 0, 'B': 0, 'R': 0, 'NA': 0, 'T': 0, 'TE': 0}
            for line in e.line_ids:
                if line[month]:
                    areas[e.source_area.id][line[month]] += 1
                    totals[line[month]] += 1
                    areas[e.source_area.id]['TE'] += 1
                    totals['TE'] += 1
                areas[e.source_area.id]['T'] += 1
                totals['T'] += 1

        for a in areas:
            areas[a]['P'] = ((float(areas[a]['G'])/float(areas[a]['TE']))*100.00) if areas[a]['TE'] else 0.00

        totals['P'] = ((float(totals['G']) / float(totals['TE'])) * 100.00) if totals['TE'] else 0.00

        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.internal_agreement_eval_docx',
            'datas': {'areas': areas, 'totals': totals}
        }
