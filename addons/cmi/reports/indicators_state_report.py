from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class IndicatorsStateReport (models.AbstractModel):
    _name = 'report.cmi.report_indicators_state_template'

    @api.model
    def render_html(self, docids, data=None):
        if data and 'date' in data and data['date']:
            date = data['date']
        else:
            date = datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT)

        company_domain = []
        if self._context.get('active_company_id'):
            company_domain.append(('company_id', '=', self._context.get('active_company_id')))

        doc = {'perspectives': [], 'no_value': []}
        indicator_ids = []
        perspectives = self.env['cmi.perspective'].search([] + company_domain)
        for perspective in perspectives:
            indicators = self.env['cmi.indicator'].search([('date', '=', date), ('perspective_id', '=', perspective.id)] + company_domain)
            indicator_ids += indicators.ids
            doc['perspectives'].append({'name': perspective.name, 'lines': indicators})

        doc['no_value'] = self.env['cmi.indicator'].search([('id', 'not in', indicator_ids)] + company_domain)

        docargs = {
            'docs': [doc],
        }
        return self.env['report'].render('cmi.report_indicators_state_template', docargs)
    


