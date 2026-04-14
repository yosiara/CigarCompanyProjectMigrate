# -*- coding: utf-8 -*-
import calendar
from datetime import date,datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.translate import _


class Period(models.Model):
    _name = "l10n_cu_period.period"
    _description = "Period"

    # COLUMNS--------------------------
    name = fields.Char('Period Name', size=32, required=True)
    annual = fields.Boolean('Annual', help="These periods can overlap.")
    date_start = fields.Date('Start of Period', required=True)
    date_stop = fields.Date('End of Period', required=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('closed', 'Closed')], 'Status', readonly=False, copy=False, default='draft',
                             help='When monthly periods are created. The status is \'Draft\'. At the end of monthly period it is in \'Done\' status.')
    # END COLUMNS--------------------------
    _sql_constraints = [
                        ('name_uniq', 'unique(name)',
                         'The name must be unique per Planification period!'),
                        ]

    @api.onchange('date_start', 'annual')
    def _onchange_date_start(self):
        res = {'value': {}}
        if self.annual and self.date_start:
            d1 = date(int(self.date_start[0:4]), int(self.date_start[5:7]), int(self.date_start[-2:]))
            after_year_date = (d1 + relativedelta(years=+1, days=-1)).strftime('%Y-%m-%d')
            res['value'] = {'date_stop': after_year_date}
        else:
            res['value'] = {'date_stop': self.date_stop}
        return res

    @api.one
    def button_reset_draft(self):
        self.state = 'draft'

    @api.one
    def button_open(self):
        self.state = 'open'

    @api.one
    def button_close(self):
        self.state = 'closed'

    @api.one
    @api.constrains('date_start', 'date_stop')
    def _check_dates(self):
        if self.date_start >= self.date_stop:
            raise ValidationError(_("The stop date of the period must be bigger than the start date!"))

        if self.annual:
            d1 = date(int(self.date_start[0:4]), int(self.date_start[5:7]), int(self.date_start[-2:]))
            after_year_date = (d1 + relativedelta(years=+1, days=-1)).strftime('%Y-%m-%d')
            if self.date_stop != after_year_date:
                raise ValidationError(_("The difference between the start date and stop date must be a year!"))

    def get_open_period(self):
        """ return open period """
        today = datetime.now()
        period_date = (today + relativedelta(days=-5)).strftime('%Y-%m-%d')
        period_id = self.search([('date_start', '<=', period_date),
                                                              ('date_stop', '>=', period_date),
                                                              ('annual', '=', False),
                                                              ('state', '=', 'open')], limit=1)
        return period_id