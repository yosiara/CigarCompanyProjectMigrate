# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _


class Obligation(models.Model):
    _name = 'enterprise_mgm_sys.obligation'

    name = fields.Text(string='Name', required=True)


class InternalAgreementLine(models.Model):
    _name = 'enterprise_mgm_sys.internal_agreement_line'

    def _get_days_selection(self):
        days = []
        for i in range(1, 32):
            days.append((str(i), str(i)))
        return days

    obligation_id = fields.Many2one('enterprise_mgm_sys.obligation', string='Obligation', required=True)
    complies_id = fields.Many2one('hr.employee', string='Complies', required=True)
    evaluates_id = fields.Many2one('hr.employee', string='Evaluates', required=True)
    day = fields.Selection(string='Day', selection=_get_days_selection, required=True, )
    internal_agreement_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.internal_agreement',
        string='Internal agreement',
        required=True, ondelete='cascade')


class InternalAgreementEvaluationLine(models.Model):
    _name = 'enterprise_mgm_sys.int_agrnt_eval_line'

    def _get_evaluations(self):
        return [('G', _('Good')), ('B', _('Bad')), ('R', _('Regular')), ('NA', _('Not Applicable'))]

    obligation_id = fields.Many2one('enterprise_mgm_sys.obligation', string='Obligation', required=True)

    complies_id = fields.Many2one('hr.employee', string='Complies', required=True)
    evaluates_id = fields.Many2one('hr.employee', string='Evaluates', required=True)
    eval_ene = fields.Selection(string='ENE', selection=_get_evaluations)
    eval_feb = fields.Selection(string='FEB', selection=_get_evaluations)
    eval_mar = fields.Selection(string='MAR', selection=_get_evaluations)
    eval_apr = fields.Selection(string='ABR', selection=_get_evaluations)
    eval_may = fields.Selection(string='MAY', selection=_get_evaluations)
    eval_jun = fields.Selection(string='JUN', selection=_get_evaluations)
    eval_jul = fields.Selection(string='JUL', selection=_get_evaluations)
    eval_aug = fields.Selection(string='AGO', selection=_get_evaluations)
    eval_sept = fields.Selection(string='SEPT', selection=_get_evaluations)
    eval_oct = fields.Selection(string='OCT', selection=_get_evaluations)
    eval_nov = fields.Selection(string='NOV', selection=_get_evaluations)
    eval_dec = fields.Selection(string='DIC', selection=_get_evaluations)
    internal_agreement_evaluation_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.internal_agreement_eval',
        string='Internal agreement',
        required=True, ondelete='cascade')


class InternalAgreement(models.Model):
    _name = 'enterprise_mgm_sys.internal_agreement'
    _rec_name = 'source_area'

    @api.multi
    @api.depends('source_area', 'destiny_area')
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, '%s - %s' % (record.source_area.name, record.destiny_area.name)))
        return result

    source_area = fields.Many2one(
        comodel_name='enterprise_mgm_sys.work_area',
        string='Area that complies',
        required=True)
    destiny_area = fields.Many2one(
        comodel_name='enterprise_mgm_sys.work_area',
        string='Area that evaluates',
        required=True)
    obligation_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.internal_agreement_line',
        inverse_name='internal_agreement_id',
        string='Obligations',
        required=True)

    @api.multi
    def _send_email_notification(self, id=None):
        day = datetime.today().day
        if id:
            internal_agreements = self.env['enterprise_mgm_sys.internal_agreement'].browse(id)
        else:
            internal_agreements = self.env['enterprise_mgm_sys.internal_agreement'].search([])

        for internal_agreement in internal_agreements:
            employees = {}
            for line in internal_agreement.obligation_ids:
                if int(line.day) == day:
                    if line.complies_id.id not in employees:
                        employees[line.complies_id.id] = {'email': line.complies_id.work_email, 'obligations': [], 'lang': line.complies_id.user_id.lang if line.complies_id.user_id else 'es_ES'}
                    employees[line.complies_id.id]['obligations'].append(line.obligation_id.name)
            for employee_id in employees:
                if employees[employee_id]['email']:
                    template = self.env.ref('enterprise_mgm_sys.email_template_obligations')
                    rendering_context = dict(self._context)
                    rendering_context.update({
                        'obligations': employees[employee_id]['obligations'],
                        'internal_agreement': internal_agreement.name,
                        'lang': employees[employee_id]['lang']
                    })
                    template = template.with_context(rendering_context)
                    template.send_mail(internal_agreement.id, False, False, {'email_to': employees[employee_id]['email']})


class InternalAgreementEvaluation(models.Model):
    _name = 'enterprise_mgm_sys.internal_agreement_eval'
    _sql_constraints = [('year_internal_agreement_id_uniq', 'unique (year, internal_agreement_id)', "There is already an evaluation for this Internal Agreement this year!")]


    @api.depends('source_area', 'destiny_area', 'year')
    def _compute_name(self):
        for record in self:
            if record.source_area and record.destiny_area:
                record.name = 'Evaluación %s - %s año %s' % (record.source_area.name, record.destiny_area.name, record.year)

    name = fields.Char('name', compute=_compute_name)
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    internal_agreement_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.internal_agreement',
        string='Internal agreement',
        required=True)
    source_area = fields.Many2one(related='internal_agreement_id.source_area', readonly=True)
    destiny_area = fields.Many2one(related='internal_agreement_id.destiny_area', readonly=True)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.int_agrnt_eval_line',
        inverse_name='internal_agreement_evaluation_id',
        string='Evaluation',
        required=False)

    @api.onchange('internal_agreement_id')
    def _onchange_process_id(self):
        list = [(6, 0, [])]
        if self.internal_agreement_id:
            for line in self.internal_agreement_id.obligation_ids:
                list.append((0, 0, {
                    'obligation_id': line.obligation_id.id,
                    'complies_id': line.complies_id.id,
                    'evaluates_id': line.evaluates_id.id,
                }))

        return {'value': {'line_ids': list}}

