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
from odoo import api, models, _, fields


class CalendarReportGroupPlanCategory(models.AbstractModel):
    _name = 'report.l10n_cu_calendar.report_group_plan_category'

    @api.multi
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        model = self.env.context.get('active_model')

        docargs = {
            'doc_ids': self._ids,
            'doc_model': model,
            'docs': data['docs'],
        }
        return report_obj.render('l10n_cu_calendar.report_group_plan_category', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
