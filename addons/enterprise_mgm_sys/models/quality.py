from odoo import fields, models, api
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime
import pytz, math


class System(models.Model):
    _name = 'enterprise_mgm_sys.system'

    name = fields.Char('Name', required=True)


class Action(models.Model):
    _name = 'enterprise_mgm_sys.action'

    name = fields.Char('Name', required=True)
    area = fields.Many2one(comodel_name='enterprise_mgm_sys.work_area', string='Area')
    participate_use_employees = fields.Boolean(
        string='Use employees on participate field',
        required=False)
    participate = fields.Text(string="Participate")
    participate_ids = fields.Many2many(comodel_name='hr.employee',
                                   relation='enterprise_mgm_sys_action_participate_employees_rel',
                                   column1='prev_plan_measure_id',
                                   column2='employee_id', string="Participate")
    compliance_date = fields.Date(string='Compliance Date', required=True)
    creation_date = fields.Date(string='Creation Date', required=False)
    cancellation_date = fields.Date(string='Cancellation Date', required=False)
    responsible_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Responsible',
        required=False)
    execute_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Execute',
        required=True)
    description = fields.Text(
        string="Description",
        required=False)
    system_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.system',
        string='System')
    type = fields.Selection(
        string='Action Type',
        selection=[('corrective', 'Corrective'), ('preventive', 'Preventive'), ('opp_improvement', 'Opportunity for improvement'), ],
        required=False, )
    improvement_program_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.improvement_program',
        string='Improvement Program',
        required=False, ondelete='cascade')
    no_conformity_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.no_conformity',
        string='No conformity',
        required=False, ondelete='cascade')
    audit_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.audit',
        string='Audit',
        required=False, ondelete='cascade')


class ImprovementProgram(models.Model):
    _name = 'enterprise_mgm_sys.improvement_program'

    def _compute_name(self):
        for record in self:
            if record.year and record.process_id:
                record.name = _('Improvement Program %s - %s') % (record.process_id.name, record.year)

    name = fields.Char(compute=_compute_name)
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    approve_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Approve',
        required=False)
    elaborates_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Elaborates',
        required=False)
    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process', required=True, ondelete='cascade')
    action_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.action',
        inverse_name='improvement_program_id',
        string='Actions',
        required=False)

    def export_to_xls(self):
        return self.env['report'].get_action(self, 'enterprise_mgm_sys.improvement_program_report', data={})


class NoConformity(models.Model):
    _name = 'enterprise_mgm_sys.no_conformity'
    _rec_name = 'no_conformity'

    @api.multi
    @api.depends('no_conformity')
    def name_get(self):
        result = []
        for record in self:
            if len(record.no_conformity) > 128:
                result.append((record.id, record.no_conformity[:125] + '...'))
            else:
                result.append((record.id, record.no_conformity))
        return result

    no_conformity = fields.Text('No conformity', required=True)
    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Area',
        required=True)
    system_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.system',
        string='System',
        required=True)
    cause = fields.Text(
        string="Cause",
        required=False)
    generic = fields.Char(
        string='Generic',
        required=False)
    unfulfilled_requirements = fields.Char(
        string='Unfulfilled Requirements',
        required=False)
    date = fields.Date(
        string='Date',
        required=True)
    plan_date = fields.Date(
        string='Planned Closing Date',
        required=False)
    closed_date = fields.Date(
        string='Closed Date',
        required=False)
    impose_on = fields.Many2one(
        comodel_name='hr.employee',
        string='Impose On',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'draft'), ('in_progress', 'In Progress'), ('accomplish', 'Accomplish'), ('unfulfilled', 'Unfulfilled')],
        required=True, default='draft')
    imposed_by = fields.Many2one(
        comodel_name='hr.employee',
        string='Imposed By',
        required=True)
    responsible_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Verification Responsible',
        required=True)
    actions_result = fields.Text(
        string="Description",
        required=False)
    observations = fields.Text(
        string="Description",
        required=False)
    action_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.action',
        inverse_name='no_conformity_id',
        string='Actions',
        required=False)
    audit_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.audit',
        string='Audit',
        required=False, ondelete='cascade')

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.no_conformity_registry_docx'
        }


class AuditResponsibilityLine(models.Model):
    _name = 'enterprise_mgm_sys.audit_resp_line'

    auditor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Auditor',
        required=True)
    responsibilities = fields.Text(
        string='Responsibilities',
        required=True)
    function = fields.Selection(
        string='Function',
        selection=[('L', 'Leader'), ('A', 'Auditor'), ],
        required=True, default='A')
    resources = fields.Text(
        string="Necessary Resources",
        required=False)
    audit_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.audit',
        string='Audit',
        required=True, ondelete='cascade')

    def get_name_str(self):
        if self.auditor_id and self.function:
            return '%s(%s)' % (self.auditor_id.name, self.function)


class AuditActivityLine(models.Model):
    _name = 'enterprise_mgm_sys.audit_activity_line'

    date = fields.Datetime(string='Date', required=True)
    activity = fields.Text(string="Activity", required=True)
    duration = fields.Float(string='Duration', required=True, default=0.00)
    place = fields.Char(string='Place', required=False)
    representative = fields.Many2one(comodel_name='hr.employee', string='Representative', required=False)
    audit_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.audit',
        string='Audit',
        required=True, ondelete='cascade')

    def format_date(self):
        timezone = pytz.timezone(self._context.get('tz') or 'UTC')
        date = pytz.UTC.localize(fields.Datetime.from_string(self.date))  # Add "+hh:mm" timezone
        date = date.astimezone(timezone)  # transform "+hh:mm" timezone
        return date.strftime("%d/%m/%Y %H:%M:%S")  # convert to string

    def format_duration(self):
        pattern = '%02d:%02d'
        value = self.duration
        if value < 0:
            value = math.abs(value)
            pattern = '-' + pattern
        hour = math.floor(value)
        min = round((value % 1) * 60)
        if min == 60:
            min = 0
            hour = hour + 1
        return pattern % (hour, min)


class Audit(models.Model):
    _name = 'enterprise_mgm_sys.audit'

    def _compute_name(self):
        for record in self:
            if record.date and record.system_id:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                record.name = _('Audit %s - %s') % (record.system_id.name, date)

    name = fields.Char(compute=_compute_name)
    date = fields.Date(string='Date', required=True)
    objective = fields.Text(string="Objective", required=True)
    scope = fields.Text(string="Scope", required=False)
    audit_criteria = fields.Text(string="Audit Criteria", required=False)
    audit_methods = fields.Text(string="Audit Methods",  required=False)
    system_id = fields.Many2one(comodel_name='enterprise_mgm_sys.system', string='System', required=True)
    auditor_leader = fields.Many2one(comodel_name='hr.employee', string='Auditor Leader', required=True)
    auditors = fields.Many2many(comodel_name='hr.employee', string='Auditors')
    audited = fields.Many2many(comodel_name='hr.employee', string='Audited')
    improvement_opportunity_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.action',
        inverse_name='audit_id',
        string='Improvement Opportunities',
        required=False)
    no_conformity_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.no_conformity',
        inverse_name='audit_id',
        string='No Conformities',
        required=False)
    state = fields.Selection(
        string='State',
        selection=[('draft', 'Draft'), ('in_progress', 'In Progress'), ('finished', 'Finished'), ],
        required=True, default='draft')
    audit_resp_line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.audit_resp_line',
        inverse_name='audit_id',
        string='Responsibilities',
        required=False)
    audit_activity_line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.audit_activity_line',
        inverse_name='audit_id',
        string='Activities',
        required=False)

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.audit_planning_docx'
        }


class InternalAuditProgramLine(models.Model):
    _name = 'enterprise_mgm_sys.int_audit_pro_line'

    process_id = fields.Many2one(comodel_name='enterprise_mgm_sys.process', string='Process', required=True, ondelete='cascade')
    months = fields.Many2many(
        comodel_name='enterprise_mgm_sys.month',
        relation='enterprise_mgm_sys_int_aud_pro_line_month_rel', column1='int_aud_pro_line_id',
        column2='month_id',
        string='Months', required=True)
    program_id = fields.Many2one(
        comodel_name='enterprise_mgm_sys.int_audit_program',
        string='Program',
        required=True, ondelete='cascade')

    def in_m(self, month):
        if self.months:
            if month in [m.number for m in self.months]:
                return True
        return False


class InternalAuditProgram(models.Model):
    _name = 'enterprise_mgm_sys.int_audit_program'

    def _compute_name(self):
        for record in self:
            if record.year:
                record.name = _('Internal Audit Program year %s') % record.year

    name = fields.Char(compute=_compute_name)
    objectives = fields.Text(string="Objectives", required=True)
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    scope = fields.Text(string="Scope", required=False)
    audit_criteria = fields.Text(string="Audit Criteria", required=False)
    audit_methods = fields.Text(string="Audit Methods",  required=False)
    resources = fields.Text(string="Necessary Resources", required=False)
    auditor_ids = fields.Many2many(comodel_name='hr.employee', string='Auditors')
    line_ids = fields.One2many(
        comodel_name='enterprise_mgm_sys.int_audit_pro_line',
        inverse_name='program_id',
        string='Planning',
        required=False)
    elaborates_id = fields.Many2one(comodel_name='hr.employee', string='Elaborates', required=False)
    approve = fields.Many2one(comodel_name='hr.employee', string='Approve', required=False)

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.internal_audit_program_docx'
        }


class InternalAuditorEval(models.Model):
    _name = 'enterprise_mgm_sys.internal_auditor_eval'

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.auditor_id and record.date:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                record.name = _('Internal Auditor Evaluation %s date %s') % (record.auditor_id.name, date)

    name = fields.Char(compute=_compute_name)
    auditor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Auditor',
        required=True)
    date = fields.Date(
        string='Date',
        required=True)
    area = fields.Many2many(comodel_name='enterprise_mgm_sys.process', relation='enterprise_mgm_sys_int_auditor_eval_process_rel', column1='internal_auditor_eval_id',
                 column2='process_id', string='Processes', required=True)
    observations = fields.Text(string="Observations", required=False)
    objectives = fields.Integer(
        string='Was able to audit all assigned targets', default=0,
        required=False)
    information = fields.Integer(
        string='Delivered the collected information on time', default=0,
        required=False)
    coherence_concordance = fields.Integer(
        string='It showed coherence, concordance and good writing', default=0,
        required=False)
    diplomacy = fields.Integer(
        string='Showed diplomacy and self-assurance', default=0,
        required=False)
    complaint = fields.Integer(
        string='There was any complaint by the auditee', default=0,
        required=False)

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.internal_auditor_evaluation_docx'
        }

    def get_eval(self):
        return self.objectives + self.information + self.coherence_concordance + self.diplomacy + self.complaint

    def get_final_eval(self):
        evaluation = self.objectives + self.information + self.coherence_concordance + self.diplomacy + self.complaint
        if evaluation == 100:
            return _('Excellent')
        elif 80 <= evaluation <= 99:
            return _('Good')
        elif 60 <= evaluation <= 79:
            return _('Regular')
        else:
            return _('Bad')

    def _get_area_string(self):
        processes = ''
        for process in self.area:
            processes += process.name + ', '
        return processes


class AuditorLeaderEval(models.Model):
    _name = 'enterprise_mgm_sys.auditor_leader_eval'

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.auditor_id and record.date:
                date = datetime.strptime(record.date, DEFAULT_SERVER_DATE_FORMAT).strftime('%d/%m/%Y')
                record.name = _('Auditor Leader Evaluation %s date %s') % (record.auditor_id.name, date)

    name = fields.Char(compute=_compute_name)
    auditor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Auditor',
        required=True)
    date = fields.Date(
        string='Date',
        required=True)
    area = fields.Many2many(comodel_name='enterprise_mgm_sys.process', relation='enterprise_mgm_sys_auditor_leader_eval_process_rel', column1='internal_auditor_eval_id',
                 column2='process_id', string='Processes', required=True)
    observations = fields.Text(
        string="Observations",
        required=False)
    audit_planning = fields.Integer(
        string='Audit Planning', default=0,
        required=False)
    communication = fields.Integer(
        string='Communication with the audit client and the audited', default=0,
        required=False)
    organization = fields.Integer(
        string='Organization and Direction of the audit team members ', default=0,
        required=False)
    guidance = fields.Integer(
        string='Guidance to auditors in training',
        required=False)
    conducting = fields.Integer(
        string='Conducting the audit team to reach the audit conclusions', default=0,
        required=False)
    conflict_prev_res = fields.Integer(
        string='Conflict prevention and resolution', default=0,
        required=False)
    audit_report = fields.Integer(
        string='Preparation and completion of the audit report', default=0,
        required=False)

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.auditor_leader_evaluation_docx'
        }

    def get_eval(self):
        return self.audit_planning + self.communication + self.organization + self.guidance + self.conducting + self.conflict_prev_res + self.audit_report

    def get_final_eval(self):
        evaluation = self.get_eval()
        if evaluation == 140:
            return _('Excellent')
        elif 105 <= evaluation <= 139:
            return _('Good')
        elif 70 <= evaluation <= 104:
            return _('Regular')
        else:
            return _('Bad')

    def _get_area_string(self):
        processes = ''
        for process in self.area:
            processes += process.name + ', '
        return processes


class InternalAuditorAnnualEval(models.Model):
    _name = 'enterprise_mgm_sys.auditor_annual_eval'

    @api.multi
    @api.depends('auditor_id')
    def _compute_audits_historical(self):
        for record in self:
            record.audits_historical = self.env['enterprise_mgm_sys.audit'].search_count(['|', ('auditor_leader', '=', record.auditor_id.id), ('auditors', 'in', record.auditor_id.id)])

    @api.multi
    def _compute_name(self):
        for record in self:
            if record.auditor_id and record.year:
                record.name = _('Internal Auditor Annual Evaluation %s year %s') % (record.auditor_id.name, record.year)

    name = fields.Char(compute=_compute_name)
    auditor_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Auditor',
        required=True)
    evaluates_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Evaluates',
        required=True)
    year = fields.Char(string='Year', required=True, default=lambda year: str(datetime.today().year))
    school_level_id = fields.Many2one('l10n_cu_hlg_hr.employee_school_level', string='School Level')
    work_experience = fields.Integer(
        string='Work Experience',
        required=False)
    audits_planned = fields.Integer(
        string='Number of Audits planned in the year',
        required=False)
    audits_carried_out = fields.Integer(
        string='Number of Audits carried out in the year',
        required=False)
    audits_historical = fields.Integer(
        string='Historical total number of audits performed',
        required=False)
    results = fields.Text(string="Results", required=False)
    final_evaluation = fields.Char(
        string='Final Evaluation',
        required=True)
    observations = fields.Text(string="Observations", required=False)

    def export_to_xls(self):
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'enterprise_mgm_sys.internal_auditor_annual_evaluation_docx'
        }











        










    


