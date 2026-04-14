# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class CapacitationPlanWizard(models.TransientModel):
    _name = 'turei_capacitacion.wzd_plan'

    @api.onchange('reports')
    def _get_domain_period(self):
        if self.reports == 'month':
            return {'domain': {'period_id': [('annual', '=', False)]}}
        else:
            return {'domain': {'period_id': [('annual', '=', True)]}}


    reports = fields.Selection([('month', 'Month'), ('year', 'Year')], string='Plan', default='month')
    period_id = fields.Many2one('l10n_cu_period.period', string='Period', required=True)


    @api.multi
    def print_plan(self):
        capacitation_action_obj = self.env['turei_capacitacion.capacitation_action']
        period_id = self.env['l10n_cu_period.period'].search([('id','=',self.period_id.id)])
        datas = {}
        capacitation_list = []


        if self.reports == 'month':
            datas['report_type'] = (_('Month Plan: %s') % (period_id.name))
            capacitation_action_ids = capacitation_action_obj.search([('start_date','>=',period_id.date_start),('end_date','<=',period_id.date_stop)])


            for capacitation_action in capacitation_action_ids:

                text = ""
                for group in capacitation_action.department_participants_ids:
                    text += tools.ustr(group.name) + ", "

                for individual in capacitation_action.individual_participants_ids:
                    text += tools.ustr(individual.name) + ", "



                data_capacitation = {
                    'name': capacitation_action.name,
                    'mode': capacitation_action.formation_mode_id.name if capacitation_action.formation_mode_id.name else '-',
                    'start_date': capacitation_action.start_date if capacitation_action.start_date else '-',
                    'end_date': capacitation_action.end_date if capacitation_action.end_date else '-',
                    'quantity': capacitation_action.quantity if capacitation_action.quantity else '-',
                    'estimate': capacitation_action.estimate if capacitation_action.estimate else '-',
                    'center': capacitation_action.formation_center_id.name if capacitation_action.formation_center_id.name else '-',
                    'description': capacitation_action.description if capacitation_action.description else '-',
                    'participants': text,
                }
                capacitation_list.append(data_capacitation)


            datas['capacitation_list'] = capacitation_list


            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'turei_capacitacion.report_plan',
                'datas': datas,
            }
        else:
            datas['report_type'] = (_('Year Plan: %s') % (period_id.name))
            capacitation_action_ids = capacitation_action_obj.search([('start_date','>=',period_id.date_start),('end_date','<=',period_id.date_stop)])\


            for capacitation_action in capacitation_action_ids:
                text = ""
                for group in capacitation_action.department_participants_ids:
                    text += tools.ustr(group.name) + ", "

                for individual in capacitation_action.individual_participants_ids:
                    text += tools.ustr(individual.name) + ", "


                data_capacitation = {
                    'name': capacitation_action.name,
                    'mode': capacitation_action.formation_mode_id.name if capacitation_action.formation_mode_id.name else '-',
                    'start_date': capacitation_action.start_date if capacitation_action.start_date else '-',
                    'end_date': capacitation_action.end_date if capacitation_action.end_date else '-',
                    'quantity': capacitation_action.quantity if capacitation_action.quantity else '-',
                    'estimate': capacitation_action.estimate if capacitation_action.estimate else '-',
                    'center': capacitation_action.formation_center_id.name if capacitation_action.formation_center_id.name else '-',
                    'description': capacitation_action.description if capacitation_action.description else '-',
                    'participants': text,
                }

                capacitation_list.append(data_capacitation)



            datas['capacitation_list'] = capacitation_list


            return {
                'type': 'ir.actions.report.xml',
                'report_name': 'turei_capacitacion.report_plan',
                'datas': datas,
            }





