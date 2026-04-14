# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class Risk(models.Model):
    _name = 'enterprise_mgm_sys.risk'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The risk you are trying to add already exists.'),
    ]

    name = fields.Char(string='Name', required=True)


class Activities(models.Model):
    _name = 'enterprise_mgm_sys.activities'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'The activity you are trying to add already exists.'),
    ]

    name = fields.Char(string='Name', required=True)


class RegistryR1Line(models.Model):
    _name = 'enterprise_mgm_sys.registryr1_line'
    _order = 'sequence,id'

    _sql_constraints = [('registry_id_risk_id_uniq', 'unique (registry_id, risk_id)', "There is already an evaluation for this risk!")]

    @api.depends('probability', 'consequence')
    @api.multi
    def _compute_level(self):
        for record in self:
            if record.probability == 'low' and record.consequence == 'low':
                record.level = 'trivial'
            elif (record.probability == 'average' and record.consequence == 'low') or (record.probability == 'low' and record.consequence == 'average'):
                record.level = 'acceptable'
            elif (record.probability == 'average' and record.consequence == 'average') or (record.probability == 'low' and record.consequence == 'high') or (record.probability == 'high' and record.consequence == 'low'):
                record.level = 'moderate'
            elif (record.probability == 'high' and record.consequence == 'high') or (record.probability == 'average' and record.consequence == 'high') or (record.probability == 'high' and record.consequence == 'average'):
                record.level = 'important'

    sequence = fields.Integer('Sequence', default=100, required=True, help='Display order')
    registry_id = fields.Many2one(comodel_name='enterprise_mgm_sys.registryr1', string='Registry', required=True, ondelete='cascade')
    risk_id = fields.Many2one(comodel_name='enterprise_mgm_sys.risk', string='Risk', required=True)
    objective = fields.Char('Objective')
    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process')
    activity_id = fields.Many2one(comodel_name='enterprise_mgm_sys.activities', string='Activity')
    classification = fields.Selection(
        string='Classification',
        selection=[('internal', 'Internal'),
                   ('external', 'External'), ],
        required=True, defualt='internal')
    probability = fields.Selection(
        string='Probability',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True)
    consequence = fields.Selection(
        string='Consequence',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True)
    level = fields.Selection(
        string='Level',
        selection=[('trivial', 'Trivial'), ('acceptable', 'Acceptable'), ('moderate', 'Moderate'),
                   ('important', 'Important')], compute=_compute_level, store=True)


class RegistryR1(models.Model):
    _name = 'enterprise_mgm_sys.registryr1'
    _description = 'Registry R1'
    rec_name = 'area_id'

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.area_id and record.date:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                if record.department_id:
                    record.name = _('Registry R1 %s-%s date %s') % (record.area_id.name, record.department_id.name, date)
                else:
                    record.name = _('Registry R1 %s date %s') % (record.area_id.name, date)

    name = fields.Char(string='Name', compute='_compute_name')
    area_id = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Segment or Unit', required=True)
    department_id = fields.Many2one(comodel_name='hr.department', string='Work Area', required=False)
    date = fields.Date(string='Date', required=True)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.registryr1_line',
        inverse_name='registry_id',
        string='Risks',
        required=False)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.registry_r1_report', data={})


class PreventivePlanMeasure(models.Model):
    _name = 'enterprise_mgm_sys.preventive_plan_measure'
    _order = 'sequence,id'

    @api.depends('probability', 'consequence')
    @api.multi
    def _compute_level(self):
        for record in self:
            if record.probability == 'low' and record.consequence == 'low':
                record.level = 'trivial'
            elif (record.probability == 'average' and record.consequence == 'low') or (record.probability == 'low' and record.consequence == 'average'):
                record.level = 'acceptable'
            elif (record.probability == 'average' and record.consequence == 'average') or (record.probability == 'low' and record.consequence == 'high') or (record.probability == 'high' and record.consequence == 'low'):
                record.level = 'moderate'
            elif (record.probability == 'high' and record.consequence == 'high') or (record.probability == 'average' and record.consequence == 'high') or (record.probability == 'high' and record.consequence == 'average'):
                record.level = 'important'

    sequence = fields.Integer('Sequence', default=100, required=True, help='Display order')
    objective = fields.Char('Objective')
    department_id = fields.Many2one(comodel_name='hr.department', string='Work Area')
    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process')
    activity_id = fields.Many2one(comodel_name='enterprise_mgm_sys.activities', string='Activity')
    risk_id = fields.Many2one(comodel_name='enterprise_mgm_sys.risk', string='Risk', required=True)
    manifestations = fields.Text(string="Possible negative manifestations", required=False)
    measures = fields.Text(string="Measures", required=False)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Responsible', required=False)
    execute_use_employees = fields.Boolean(
        string='Use employees on execute field',
        required=False)
    execute = fields.Text(string="Execute")
    execute_ids = fields.Many2many(comodel_name='hr.employee',
                                   relation='enterprise_mgm_sys_prev_plan_measure_employees_rel',
                                   column1='prev_plan_measure_id',
                                   column2='employee_id', string="Execute")
    compliance_dates = fields.Char(string="Compliance Dates", required=False,
                                   help="Dates list separated by comma for example '25/12/2019,05/07/2020'.")
    state = fields.Selection([('new', 'New'), ('fulfilled', 'Fulfilled'), ('unfulfilled', 'Unfulfilled')],
                             string='Status', default='new')
    classification = fields.Selection(
        string='Classification',
        selection=[('internal', 'Internal'),
                   ('external', 'External'), ],
        required=True, default='internal')
    probability = fields.Selection(
        string='Probability',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True)
    consequence = fields.Selection(
        string='Consequence',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True)
    level = fields.Selection(
        string='Level',
        selection=[('trivial', 'Trivial'), ('acceptable', 'Acceptable'), ('moderate', 'Moderate'),
                   ('important', 'Important')], compute=_compute_level, store=True)
    plan_id = fields.Many2one(comodel_name='enterprise_mgm_sys.risks_prevention_plan', string='Plan', required=True,
                              ondelete='cascade')


class RisksPreventionPlan(models.Model):
    _name = 'enterprise_mgm_sys.risks_prevention_plan'
    rec_name = 'area_id'

    _sql_constraints = [
        ('area_year_uniq', 'unique(area_id,year)', 'There is already a prevention plan for this area this year.'),
    ]

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.all_company and record.year:
                record.name = _('Registry R2 Enterprise year %s') % record.year
            elif record.area_id and record.year:
                record.name = _('Registry R2 area %s year %s') % (record.area_id.name, record.year)

    name = fields.Char(string='Name', compute='_compute_name')
    all_company = fields.Boolean(string='All Company', default=False, required=True)
    area_id = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Segment or Unit')
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    date = fields.Date(string='Elaboration Date', required=True, default=lambda d: datetime.today())
    measure_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.preventive_plan_measure',
        inverse_name='plan_id', string='Measures', required=False)

    @api.model
    def create(self, vals):
        start = datetime(int(vals['year']), 1, 1).strftime(DEFAULT_SERVER_DATE_FORMAT)
        stop = datetime(int(vals['year']), 12, 31).strftime(DEFAULT_SERVER_DATE_FORMAT)

        if vals['all_company']:
            r1s = self.env['enterprise_mgm_sys.registryr1'].search(
                [('date', '<=', stop), ('date', '>=', start)])
        else:
            r1s = self.env['enterprise_mgm_sys.registryr1'].search(
                [('date', '<=', stop), ('date', '>=', start), ('area_id', '=', vals['area_id'])])

        cmd = [(6, 0, [])]
        risks = {}
        for r1 in r1s:
            for risk in r1.line_ids:
                if risk.risk_id.id in risks:
                    continue
                else:
                    risks[risk.risk_id.id] = True
                cmd.append((0, 0, {
                    'department_id': r1.department_id.id if r1.department_id else False,
                    'objective': risk.objective,
                    'process_id': risk.process_id.id,
                    'activity_id': risk.activity_id.id,
                    'risk_id': risk.risk_id.id,
                    'probability': risk.probability,
                    'consequence': risk.consequence,
                    'level': risk.level,
                }))

        vals.update({'measure_ids': cmd})
        return super(RisksPreventionPlan, self).create(vals)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.risks_prevention_plan_report', data={})

    def export_r5_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.control_compliance_measures_report', data={})


class BehaviorPreventionPlanLine(models.Model):
    _name = 'enterprise_mgm_sys.beh_prev_plan_line'

    objective = fields.Char(string='Objective', required=True)
    measures_not_complied = fields.Char(string='Measures not complied', help='Description of the measures not complied',
                                        required=True)
    observations = fields.Char(string='Observations')
    action = fields.Selection(
        string='Action to develop',
        selection=[('keep', 'Keep'), ('delete', 'Delete'), ('modify', 'Modify'), ('incorporate', 'Incorporate new')],
        required=True)
    plan_id = fields.Many2one(comodel_name='enterprise_mgm_sys.behavior_prevention_plan', string='Plan', required=True, ondelete='cascade')


class BehaviorPreventionPlan(models.Model):
    _name = 'enterprise_mgm_sys.behavior_prevention_plan'

    @api.constrains('objectives_amount', 'measures_approved')
    def constrains_objective_measures(self):
        if not self.objectives_amount or not self.measures_approved:
            raise ValidationError(_('The amount of objectives and measures planned have to be greater than zero.'))

    @api.depends('objectives_met', 'objectives_amount', 'measures_accomplished', 'measures_approved')
    @api.multi
    def _compute_efficacy(self):
        for record in self:
            record.efficacy = (record.objectives_met / record.objectives_amount - (
                    1 - record.measures_accomplished / record.measures_approved) * 0.8) * 100

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.area_id and record.date:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                record.name = _('Registry R3 %s date %s') % (record.area_id.name, date)

    name = fields.Char(string='Name', compute='_compute_name')
    area_id = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Segment or Unit', required=True)
    date = fields.Date(string='Date', required=True)
    objectives_amount = fields.Integer('Objectives approved for the year')
    objectives_met = fields.Integer('Objectives met', help='Objectives met to date')
    objectives_unfulfilled = fields.Integer('Unfulfilled objectives', help='Unfulfilled objectives to date')
    objectives_not_evaluated = fields.Integer('Objectives not evaluated',
                                              help='Number of Objectives not evaluated to date')
    measures_approved = fields.Integer('Measures approved',
                                       help='Measures approved in the risk prevention and management plan')
    measures_month = fields.Integer('Measures for the month', help='Measures to be carried out in the month')
    measures_accomplished = fields.Integer('Measures accomplished')
    measures_unfullfilled = fields.Integer('Unfullfilled Measures')
    change_detection = fields.Text('Change detection')
    proposed_agreements = fields.Text('Proposed agreements')
    evaluated_incidents = fields.Text('Evaluated Incidents')
    objective_foundation = fields.Text('Objective Foundation')
    elaborates_id = fields.Many2one(comodel_name='hr.employee', string='Elaborates', required=False)
    approve_id = fields.Many2one(comodel_name='hr.employee', string='Approve', required=False)
    efficacy = fields.Float(string='Efficacy', required=False)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.beh_prev_plan_line',
        inverse_name='plan_id',
        string='Behavior',
        required=False)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.behavior_prevention_plan_report', data={})


class ControlMeasuresEfficacyLine(models.Model):
    _name = 'enterprise_mgm_sys.ctrl_measures_efficacy_line'

    objective = fields.Char(string='Objective', required=True)
    compliance = fields.Selection(string='Compliance', selection=[('yes', 'Yes'), ('no', 'No'), ], default='yes',
                                  required=True)
    risk_id = fields.Many2one(comodel_name='enterprise_mgm_sys.risk', string='Risk', required=True)
    classification = fields.Selection(
        string='Classification',
        selection=[('internal', 'Internal'),
                   ('external', 'External'), ],
        required=True, defualt='internal')
    probability = fields.Selection(
        string='Probability',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True, default='low')
    consequence = fields.Selection(
        string='Consequence',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True, default='low')
    level = fields.Selection(
        string='Level',
        selection=[('trivial', 'Trivial'), ('acceptable', 'Acceptable'), ('moderate', 'Moderate'),
                   ('important', 'Important')],
        required=True, )
    measures = fields.Text(string="Measures")
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Responsible')
    compliance_dates = fields.Char(string="Compliance Dates", required=False, help="Dates list separated by comma.")
    new_probability = fields.Selection(
        string='New Probability',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True, default='low')
    new_consequence = fields.Selection(
        string='New Consequence',
        selection=[('low', 'Low'), ('average', 'Average'), ('high', 'High')],
        required=True, default='low')
    new_level = fields.Selection(
        string='New Level',
        selection=[('trivial', 'Trivial'), ('acceptable', 'Acceptable'), ('moderate', 'Moderate'),
                   ('important', 'Important')],
        required=True)
    control_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.control_measures_efficacy',
        string='Control',
        required=True, ondelete='cascade')


class ControlMeasuresEfficacy(models.Model):
    _name = 'enterprise_mgm_sys.control_measures_efficacy'

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.area_id and record.date:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                record.name = _('Registry R4 %s date %s') % (record.area_id.name, date)

    name = fields.Char(string='Name', compute='_compute_name')
    area_id = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Segment or Unit', required=True)
    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process', required=True)
    date = fields.Date(string='Date', required=True)
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.ctrl_measures_efficacy_line',
        inverse_name='control_id',
        string='Efficacy',
        required=False)

    @api.model
    def create(self, vals):
        date = datetime.strptime(vals['date'], DEFAULT_SERVER_DATE_FORMAT)

        measures = self.env['enterprise_mgm_sys.preventive_plan_measure'].search(
            [('plan_id.year', '=', str(date.year)), ('process_id', '=', vals['process_id']),
             ('plan_id.area_id', '=', vals['area_id'])])

        cmd = [(6, 0, [])]
        for measure in measures:
            cmd.append((0, 0, {
                'objective': measure.objective,
                'risk_id': measure.risk_id.id,
                'classification': measure.classification,
                'probability': measure.probability,
                'consequence': measure.consequence,
                'level': measure.level,
                'new_probability': measure.probability,
                'new_consequence': measure.consequence,
                'new_level': measure.level,
                'measures': measure.measures,
                'employee_id': measure.employee_id.id,
                'compliance_dates': measure.compliance_dates,
            }))

        vals.update({'line_ids': cmd})
        return super(ControlMeasuresEfficacy, self).create(vals)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.control_measures_efficacy_report', data={})
