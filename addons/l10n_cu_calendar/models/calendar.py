# -*- coding: utf-8 -*-


from odoo import api, fields, models, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, relativedelta
import logging
import pytz
import re
import time
from dateutil import parser
from dateutil import rrule

from datetime import datetime, date, timedelta
from odoo.addons.calendar.models.calendar import VIRTUALID_DATETIME_FORMAT
from odoo.addons.calendar.models.calendar import calendar_id2real_id, Meeting as OdooMeeting

_logger = logging.getLogger(__name__)
resp_dic = {'nokey': _ ( 'Debe solicitar una clave de registro. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' ),
            'invalidkey': _ ( 'Está utilizando una clave no válida. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' ),
            'expkey': _ ( 'Está utilizando una clave caducada. Póngase en contacto con el centro de soporte técnico, a través de la dirección de correo comercial.holguin@desoft.cu para obtener una nueva.' )}

def _is_date_time_saving(actual_date):
    assert actual_date.tzinfo is not None
    assert actual_date.tzinfo.utcoffset(actual_date) is not None
    return bool(actual_date.dst())


class CalendarTaskCategory(models.Model):
    _name = "l10n_cu_calendar.task_category"
    _description = "Task category"
    _order = 'code'

    # COLUMNS--------------------------
    name = fields.Char('Category', size=600, required=True)
    parent_id = fields.Many2one('l10n_cu_calendar.task_category', string='Parent Category')
    child_ids = fields.One2many('l10n_cu_calendar.task_category', 'parent_id', string='Child Categories')
    code = fields.Char('Code', size=10, required=True, index=True)
    objective_ids = fields.One2many('l10n_cu_calendar.objective_task', 'category_id', string='Objectives')
    task_ids = fields.One2many('calendar.event', 'category_id', string='Tasks')

    _sql_constraints = [('name_uniq', 'unique(name)', _(u'El nombre de la categoría debe ser único.')),
                        ('task_category_code_uniq', 'unique(code)', _(u'El código de la categoría debe ser único.'))]

    # Comentareado, para poder importar en el data las categorías
    # @api.one
    # @api.constrains('name')
    # def check_reg(self):
    #     resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_calendar')
    #     if resp != 'ok':
    #         raise ValidationError(resp_dic[resp])

    def has_task(self, group_id, date_start, date_end, ids=None):
        domain = [('attendees_group_ids', 'in', group_id), ('category_id', '=', self.id),
             ('stop', '>=', date_start), ('start', '<=', date_end)]
        if ids:
            domain.append(('id', 'in', ids))
        events = self.env['calendar.event'].search(domain)
        if events:
            return True

        for cat in self.child_ids:
            if cat.has_task(group_id=group_id, date_start=date_start, date_end=date_end, ids=ids):
                return True
        return False


class Guideline(models.Model):
    _name = 'l10n_cu_calendar.guideline'
    _description = "Guideline"
    _order = 'number'

    name = fields.Char('Guideline', required=True)
    number = fields.Integer('Number', required=True)
    objective_ids = fields.Many2many('l10n_cu_calendar.objective_task', 'l10n_cu_calendar_objective_guideline',
                                     'guideline_id', 'objective_id', string='Objectives')


class CalendarObjective(models.Model):
    _name = 'l10n_cu_calendar.objective_task'
    _description = "Task's objectives"
    _order = 'code'

    def _compute_allowed_groups(self):
        model_config = self.env['res.groups'].fields_get()
        if model_config['name']['translate']:
            group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Manager')
        else:
            group_name = _('Calendar Manager')

        groups = self.env['res.groups'].search([('name', '=', group_name)])
        users = []
        for u in groups.users:
            users.append(u.id)

        # If user have Calendar Manager Rol have all Rights
        if self.env.user.id in users:
            return []
        elif self.env.user.id not in users:
            if model_config['name']['translate']:
                group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Limited Calendar Manager')
            else:
                group_name = _('Limited Calendar Manager')

            groups = self.env['res.groups'].search([('name', '=', group_name)])
            users = []
            for u in groups.users:
                users.append(u.id)

            # If user have Limited Calendar Manager Rol have all Rights
            if self.env.user.id in users:
                return []

        groups = self.env['l10n_cu_calendar.org_group']
        ids = groups.search([('partner_id.id', '=', self.env.user.partner_id.id)])
        return [('id', 'in', ids.ids)]

    # ---------------COLUMNS---------------------
    name = fields.Text('Objective', size=600, required=True, index=True)
    code = fields.Char('Code', size=10, required=True, index=True)
    parent_id = fields.Many2one('l10n_cu_calendar.objective_task', string='Parent')
    child_ids = fields.One2many('l10n_cu_calendar.objective_task', 'parent_id', string='Child Objectives')
    category_id = fields.Many2one('l10n_cu_calendar.task_category', string='Category', required=True)
    task_ids = fields.One2many('calendar.event', 'objective_id', string='Tasks')
    group_id = fields.Many2one('l10n_cu_calendar.org_group', string='Area', domain=_compute_allowed_groups,
                               required=True)
    period_id = fields.Many2one('l10n_cu_period.period', string='Period', domain="[('annual', '=', True)]",
                                required=True)
    # group_id = fields.Many2one('l10n_cu_calendar.org_group', string='Area', domain=_compute_allowed_groups, required=True)
    # period_id = fields.Many2one('l10n_cu_period.period', string='Period', domain="[('annual', '=', True)]", required=True)
    guideline_ids = fields.Many2many('l10n_cu_calendar.guideline', 'l10n_cu_calendar_objective_guideline',
                                     'objective_id', 'guideline_id', string='Guidelines')
    # ---------------END COLUMNS------------------

    _constraints = [(models.BaseModel._check_recursion,
                     'No está permitido relacionar el objetivo con el mismo objetivo, en el Objetivo superior.',
                     ['parent_id'])]

    def _compute_allowed_groups(self):
        model_config = self.env['res.groups'].fields_get()
        if model_config['name']['translate']:
            group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Manager')
        else:
            group_name = _('Calendar Manager')

        groups = self.env['res.groups'].search([('name', '=', group_name)])
        users = []
        for u in groups.users:
            users.append(u.id)

        # If user have Calendar Manager Rol have all Rights
        if self.env.user.id in users:
            return []

        groups = self.env['l10n_cu_calendar.org_group']
        ids = groups.search([('partner_id.id', '=', self.env.user.partner_id.id)])
        return [('id', 'in', ids.ids)]

    _sql_constraints = [('name_uniq', 'unique(name)', _(u'El nombre del objetivo debe ser único.'))]

    @api.one
    @api.constrains('name')
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_calendar')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

    def has_task(self, group_id, date_start, date_end, ids=None):
        domain = [('attendees_group_ids', 'in', group_id), ('objective_id', '=', self.id),
             ('stop', '>=', date_start), ('start', '<=', date_end)]
        if ids:
            domain.append(('id', 'in', ids))
        events = self.env['calendar.event'].search(domain)
        if events:
            return True

        for obj in self.child_ids:
            if obj.has_task(group_id=group_id, date_start=date_start, date_end=date_end):
                return True
        return False

    def get_guidelines_str(self):
        i = 0
        guidelines = "Lineamientos "
        for g in self.guideline_ids:
            if i == 0:
                guidelines += str(g.number)
            else:
                guidelines += (', ' + str(g.number))
            i += 1
        return guidelines


class CalendarCategoryObjectiveLine(models.Model):
    _name = 'l10n_cu_calendar.category_objective_line'

    task_id = fields.Many2one('calendar.event', string='Task', required=True)
    category_id = fields.Many2one('l10n_cu_calendar.task_category', string='Category', required=True)
    objective_id = fields.Many2one('l10n_cu_calendar.objective_task', string='Objective', required=True)
    guidelines = fields.Char(string='Guidelines', compute='_compute_guidelines', store=True)

    @api.one
    @api.depends('objective_id')
    def _compute_guidelines(self):
        i = 0
        guidelines = ""
        if self.objective_id:
            for g in self.objective_id.guideline_ids:
                if i == 0:
                    guidelines = str(g.number)
                else:
                    guidelines += (', ' + str(g.number))
                i += 1
        self.guidelines = guidelines


class CalendarOrgGroup(models.Model):
    _name = 'l10n_cu_calendar.org_group'
    _description = "Organizations groups"

    @api.onchange('department_id')
    def onchange_department_id(self):
        if not self.department_id:
            return {}
        department = self.department_id
        member_list = []
        for emp in department.member_ids:
            if emp.user_id:
                member_list.append(emp.user_id.partner_id.id)

        return {'value': {'name': department.name,
                          'partner_id': department.manager_id.user_id.partner_id.id,
                          'partner_group_ids': [(6, 0, member_list)],
                          'work_plan': True
                          }
                }

    # COLUMNS--------------------------
    name = fields.Char('Name', size=128, required=True, index=True, )
    department_id = fields.Many2one('hr.department', string="Related department")
    partner_id = fields.Many2one('res.partner', string="Group's chief", domain="[('employee','=',True)]")
    parent_id = fields.Many2one('l10n_cu_calendar.org_group', string='Parent')
    childs_ids = fields.One2many('l10n_cu_calendar.org_group', 'parent_id', string='Childs')
    partner_group_ids = fields.Many2many('res.partner', 'l10n_cu_calendar_org_group_partner_group', 'group_id',
                                         'partner_id', string='Miembros', domain="[('employee','=',True)]")
    work_plan = fields.Boolean(string='Work Plan', help='Mark this checkbox if this group must have a work plan.', )
    cant = fields.Integer('Quantity', compute='_compute_cant')
    group_type = fields.Selection([('simple', 'Simple'), ('integrated', 'Integrated')], 'Group Type',
                                  index=True, default='simple',
                                  help="""If the group is "simple" you must define the members of the group.
                                        If the group is composed you must define the groups that compose it.""")

    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True,
                                 default=lambda self: self.env['res.company']._company_default_get(
                                     'l10n_cu_calendar.org_group'))
    include_single_members = fields.Boolean('Include members')
    single_member_ids = fields.Many2many('res.partner', 'l10n_cu_calendar_org_group_single_member', 'group_id',
                                         'partner_id', string='Other members')

    @api.onchange('childs_ids')
    def _onchange_partner_group_ids(self):
        partnerlist = self.GetPartnerInGroup(self)
        return {'domain': {'single_member_ids': [('employee', '=', True), ('id', 'not in', partnerlist)]}}

    # END COLUMNS-------------------------Esto es un pie porque no se quiere traducir
    _sql_constraints = [('name_uniq', 'unique(name)', _(u'El nombre del grupo organizativo debe ser único.'))]

    @api.one
    @api.constrains('name')
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_calendar')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

    @api.multi
    def _compute_cant(self):
        for group in self:
            group.cant = len(group.partner_group_ids)

    # Abrir calendar del grupo
    @api.multi
    def view_calendar(self):
        domain = []

        if self._ids[0]:
            domain = [('attendees_group_ids', 'in', self._ids[0])]

        return {
            'type': 'ir.actions.act_window',
            'name': self.name,
            'res_model': 'calendar.event',
            'view_type': 'form',
            'view_mode': 'calendar,tree,form',
            'target': 'current',
            'domain': domain,
            'nodestroy': True
        }

    @api.multi
    def update_superior(self):
        for group in self:
            # buscar el jefe del grupo
            if group.partner_id:
                group_boss = group.partner_id.id
                # buscar el empleado del grupo organizativo a traves de usuario
                user = self.env['res.users'].search([('partner_id', '=', group_boss)])
                employee_boss = False
                if user:
                    employee_boss = self.env['hr.employee'].search([('user_id', '=', user[0].id)])
                # Actualizar el superior en los integrantes del grupo
                for partner in group.partner_group_ids:
                    if group_boss != partner.id:
                        partner.write({'boss_id': group_boss})
                        # Actualizar el superior del empleado correspondiente a este partner
                        user_employee = self.env['res.users'].search([('partner_id', '=', partner.id)])
                        if user_employee:
                            employee = self.env['hr.employee'].search([('user_id', '=', user_employee[0].id)])
                            employee.write({'parent_id': employee_boss[0].id if employee_boss[0] else False})
                        else:
                            raise ValidationError(
                                _(
                                    'Error! El usuario %s debe estar asociado a un empleado para actualizarle el superior.' % (
                                        partner.name)))
            else:
                raise ValidationError(
                    _('Error! Para actualizar el superior se debe definir el responsable del grupo.'))
        return True

    def GetPartnerInGroup(self, group):
        """ group:param object
        :return list of partner in this group"""
        partnerlist = []
        if group.group_type == 'integrated':
            partnerlist += group.single_member_ids.ids
            for child_group in group.childs_ids:
                partnerlist += self.GetPartnerInGroup(child_group)
        else:
            for partner in group.partner_group_ids:
                if partner.id not in partnerlist:
                    partnerlist.append(partner.id)
        return partnerlist

    # @api.onchange('childs_ids')
    # def OnChangeChildsGroups(self):
    #     partnerlist = self.GetPartnerInGroup(self)
    #     cmds = [(6, False, partnerlist)]
    #     self.partner_group_ids = cmds

    # def UpdateMembersInGroup(self, group):
    #     partnerlist = self.GetPartnerInGroup(group)
    #     res = [(6, 0, partnerlist)]
    #     group.write({'partner_group_ids': res})
    #     return True

    @api.one
    def write(self, vals):
        res = super(CalendarOrgGroup, self).write(vals)
        if (('group_type' in vals and vals['group_type'] != 'simple') or (
                'group_type' not in vals and self.group_type != 'simple')) and 'childs_ids' in vals:
            partnerlist = self.GetPartnerInGroup(self)
            self.write({'partner_group_ids': [(6, False, partnerlist)]})
        elif ('group_type' in vals and vals['group_type'] == 'simple') or (
                'group_type' not in vals and self.group_type == 'simple') and not self._context.get('clear_childs'):
            self.with_context(clear_childs=True).write({'childs_ids': [(6, False, [])]})

        return res

    def UpdateMembers(self):
        partnerlist = self.GetPartnerInGroup(self)
        self.write({'partner_group_ids': [(6, 0, partnerlist)]})


class Attendee(models.Model):
    _inherit = 'calendar.attendee'
    _description = "Attendee information"
    _order = "date_start asc"

    date_start = fields.Datetime(related='event_id.start', store=True, readonly=True)
    recurrency = fields.Boolean(related='event_id.recurrency', store=True, readonly=True)
    type = fields.Selection(related='event_id.type', store=True, readonly=True)
    user_id = fields.Many2one('res.users', 'User', readonly="True")
    cause = fields.Char('Cause', size=128, index=True)

    state = fields.Selection(selection_add=[('done', 'Done'),
                                            ('not_done', 'Not Done')], string='Status', readonly=True,
                             default='accepted')
    active_task_list = fields.Boolean('Active My Task list', compute='_compute_active_task_list', store=True)

    @api.multi
    def task_done(self):
        """ Makes event participation as done """
        for attendee in self:
            if attendee.event_id.state == 'fulfilled' or attendee.event_id.state == 'unfulfilled':
                raise ValidationError(_('You can not evaluate a closed event. Contact with event responsible to open.'))
            else:
                attendee.write({'state': 'done'})
        return True

    @api.multi
    def task_not_done(self):
        """ The partner don't participate lklin this event  """
        for attendee in self:
            if attendee.event_id.state == 'fulfilled' or attendee.event_id.state == 'unfulfilled':
                raise ValidationError(_('You can not evaluate a closed event. Contact with event responsible to open.'))
            else:
                attendee.write({'state': 'not_done', 'cause': 'Ausente'})
        return True

    @api.multi
    def _send_mail_to_attendees(self, template_xmlid, force_send=False):
        if template_xmlid == 'calendar.calendar_template_meeting_invitation':
            template_xmlid = 'l10n_cu_calendar.calendar_template_meeting_invitation'
        elif template_xmlid == 'calendar.calendar_template_meeting_changedate':
            template_xmlid = 'l10n_cu_calendar.calendar_template_meeting_changedate'
        elif template_xmlid == 'calendar.calendar_template_meeting_reminder':
            template_xmlid = 'l10n_cu_calendar.calendar_template_meeting_reminder'
        return super(Attendee, self)._send_mail_to_attendees(template_xmlid, force_send)

    @api.multi
    def do_decline(self):
        """ Marks event invitation as Declined. """
        for attendee in self:
            res = self.write({'state': 'declined'})
            attendee.event_id.message_post(body=_("%s has declined invitation") % (attendee.common_name),
                                           subtype="calendar.subtype_invitation")
            event = self.env['calendar.event'].search([('id', '=', attendee.event_id.id)])
            a = event.write({'partner_ids': [(3, attendee.partner_id.id, None)]})
            # print a
            return res

    @api.multi
    @api.depends('recurrency', 'event_id.active')
    def _compute_active_task_list(self):
        for att in self:
            if att.recurrency or len(str(att.event_id).split('-')) != 1:
                att.active_task_list = False
            att.active_task_list = att.event_id.active


# --------------------------------------
#    ALARM
# --------------------------------------
class Alarm(models.Model):
    _inherit = 'calendar.alarm'

    _sql_constraints = [('calendar_alarm_name_uniq', 'unique(name)', _(u'El nombre de la alarma debe ser único.'))]


# --------------------------------------
#    TASK
# --------------------------------------
class Meeting(models.Model):
    _inherit = 'calendar.event'
    _description = "Task"
    _order = "priority_order, start, id desc"

    # ----COLUMNS-------------------------------------------
    objective_id = fields.Many2one('l10n_cu_calendar.objective_task', string="Objective")
    category_id = fields.Many2one('l10n_cu_calendar.task_category', string="Category")
    local_id = fields.Many2one('l10n_cu_locals.local', string="Local", track_visibility='onchange')
    # grupos seleccionados por el usuario que crea la tarea
    group_ids = fields.Many2many('l10n_cu_calendar.org_group', 'l10n_cu_calendar_select_groups', 'task_id', 'group_id',
                                 string='Attendee Groups')
    individual_attendee_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Individual Attendee', relation='l10n_cu_calendar_calendar_event_indi_att_rel')
    # grupos relacionados con plan de trabajo debido a los participantes en la tarea
    attendees_group_ids = fields.Many2many('l10n_cu_calendar.org_group', 'l10n_cu_calendar_task_groups', 'task_id',
                                           'group_id', string='Affected Groups')
    priority = fields.Selection([('0', 'Low'), ('1', 'Normal'), ('2', 'High')], 'Priority', index=True, default='1')
    type = fields.Selection([('plan', 'Plan'), ('extra', 'Extra Plan')], 'Type', index=True, default='plan')
    behave = fields.Selection([('assign_specific', 'Specific Assign'), ('assign_auto', 'Automatic Assign'),
                               ], 'Behave', index=True, default='assign_specific')
    group_task = fields.Boolean(string='Group Task', help='Mark this checkbox if this task is a group task.',
                                default=False)
    directed_by_job = fields.Char('Directed by(job)', size=128, required=True, index=True, default='Cargo no definido')
    participants_text = fields.Text('Task participants to show in plan', required=False, default='')

    duration = fields.Float('Duration', states={'done': [('readonly', True)]}, default=1.0)
    mail_notification = fields.Boolean(string='Mail notification',
                                       help='Mark this checkbox for automatic mail notification.', default=False)
    repeat_other_year = fields.Boolean(string='Repeat other year',
                                       help='Mark this checkbox if this task could be repeat other year.')
    repeat_id = fields.Integer(string='Repeat id')
    attendee_status = fields.Selection(selection_add=[('done', 'Done'),
                                                      ('not_done', 'Not Done')], string='Attendee Status',
                                       compute='_compute_attendee')
    edit = fields.Boolean(string='User edit', help='User can edit this event', compute='_compute_access', default=True)
    add_responsible = fields.Boolean(string='Add Responsible', help='Add responsible automatic to attendees',
                                     default=False)
    only_employee = fields.Boolean(string='Only employee', help='Only show employees users.', default=True)
    state = fields.Selection(selection_add=[('fulfilled', 'Fulfilled'), ('unfulfilled', 'Unfulfilled')],
                             string='Status', readonly=True,
                             help="Stados de la tarea")
    guidelines = fields.Char(string='Guidelines', compute='_compute_guidelines')
    week_list = fields.Selection([
        ('MO', 'Monday'),
        ('TU', 'Tuesday'),
        ('WE', 'Wednesday'),
        ('TH', 'Thursday'),
        ('FR', 'Friday'),
        ('SA', 'Saturday'),
        ('SU', 'Sunday')
    ], string='Weekday', default='MO')
    byday = fields.Selection([
        ('1', 'First'),
        ('2', 'Second'),
        ('3', 'Third'),
        ('4', 'Fourth'),
        ('5', 'Fifth'),
        ('-1', 'Last')
    ], string='By day', default='1')

    end_type = fields.Selection([
        ('count', '# of repetitions'),
        ('end_date', 'End date')
    ], string='Recurrence Termination', default='count')
    unfulfilled_cause = fields.Text(string='Non-fulfillment cause')
    add_anyway = fields.Boolean(string='Matching Schedule', default=False)
    needs_assurance = fields.Boolean(string='Needs Assurance', default=False)
    parent_id = fields.Many2one('calendar.event', string='Main Task')
    child_ids = fields.One2many('calendar.event', 'parent_id', string='Assurance Tasks')
    unfulfilled_origin = fields.Many2one('res.partner', 'Non-fulfillment origin')
    modification_origin = fields.Many2one('res.partner', 'Modification origin')
    extra_plan_origin = fields.Many2one('res.partner', 'Extra plan-Origin')
    modification_cause = fields.Text('Modification cause')
    extra_plan_cause = fields.Text('Extra plan-Cause')
    color_key = fields.Integer('Color Key', compute='_compute_color_key')
    hide_time_in_report = fields.Boolean('Hide time in report', default=False, )
    priority_order = fields.Integer('Priority order', default=100, help='The priority of the task, as an integer: 0 means higher priority, 10 means lower priority.')
    short_name = fields.Char(string='Nombre corto', size=20)


    # -------------------------------------------------------

    @api.constrains('child_ids')
    def _validate_child_ids(self):
        if self.recurrency and self.child_ids:
            raise ValidationError(_('You can not create assurance tasks for a recurrent task.'))
        for record in self.child_ids:
            if record.recurrency:
                raise ValidationError(_('The assurance tasks can not be recurrent.'))

    # @api.constrains('category_id')
    # def _validate_category_id(self):
    #     for record in self.child_ids:
    #         if record.category_id != self.category_id:
    #             raise ValidationError(_('The category of an assurance task can not differ from the category of the main task.'))

    @api.multi
    @api.depends('recurrency')
    def _compute_color_key(self):
        for record in self:
            if record.recurrency:
                record.color_key = 16
            else:
                record.color_key = 11

    @api.one
    @api.depends('objective_id')
    def _compute_guidelines(self):
        i = 0
        guidelines = ""
        if self.objective_id:
            for g in self.objective_id.guideline_ids:
                if i == 0:
                    guidelines = str(g.number)
                else:
                    guidelines += (', ' + str(g.number))
                i += 1
        self.guidelines = guidelines

    @api.model
    def participants_char(self, onchage=False):
        """ Convert participants to char format to use in report"""
        if onchage or (not onchage and not self.participants_text):
            l = []
            jobs_added = {}
            if self.env.user.company_id.show_jobs_on_plan and self.user_id.partner_id.function:
                responsible_id = self.user_id.partner_id.function
            else:
                responsible_id = self.user_id.partner_id.name
            if self.behave == "assign_specific":
                for p in self.partner_ids:
                    if self.env.user.company_id.show_jobs_on_plan and p.function:
                        if p.function not in jobs_added:
                            l.append(p.function)
                            jobs_added[p.function] = True
                    else:
                        l.append(p.name)
                if len(l) > 1 and responsible_id in l:
                    l.remove(responsible_id)

            if self.behave == "assign_auto":
                groups = self.group_ids.sudo() if onchage else self.sudo().group_ids
                for g in groups:
                    l.append(g.name)
                for p in self.individual_attendee_ids:
                    if self.env.user.company_id.show_jobs_on_plan and p.function:
                        l.append(p.function)
                    else:
                        l.append(p.name)

            text = ""
            i = 0
            for name in l:
                text += tools.ustr(name) + ", "
                i += 1
            return text
        else:
            return self.participants_text

    @api.multi
    @api.depends('allday', 'start', 'stop')
    def _compute_dates(self):
        for meeting in self:
            if meeting.allday:
                tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                if meeting.start[11:19] == '00:00:00':
                    startdate = fields.Datetime.from_string(meeting.start)
                    startdate = tz.localize(startdate)  # Add "+hh:mm" timezone
                    startdate = startdate.replace(hour=12)  # Set 12 AM in localtime to avoid change of date when this sate is localized
                    startdate = startdate.astimezone(pytz.utc)  # Convert to UTC
                    meeting.start = fields.Datetime.to_string(startdate)
                meeting.start_date = meeting.start
                meeting.start_datetime = False

                if meeting.stop[11:19] == '00:00:00':
                    enddate = fields.Datetime.from_string(meeting.stop)
                    enddate = tz.localize(enddate)
                    enddate = enddate.replace(hour=12) # Set 12 AM in localtime to avoid change of date when this sate is localized
                    enddate = enddate.astimezone(pytz.utc)
                    meeting.stop = fields.Datetime.to_string(enddate)
                meeting.stop_date = meeting.stop
                meeting.stop_datetime = False
                meeting.duration = 0.0
            else:
                meeting.start_date = False
                meeting.start_datetime = meeting.start
                meeting.stop_date = False
                meeting.stop_datetime = meeting.stop
                meeting.duration = self._get_duration(meeting.start, meeting.stop)

    @api.multi
    def _inverse_dates(self):
        for meeting in self:
            if meeting.allday:
                tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc

                enddate = fields.Datetime.from_string(meeting.stop_date)
                enddate = tz.localize(enddate)
                enddate = enddate.replace(hour=12) # Set 12 AM in localtime to avoid change of date when this date is localized
                enddate = enddate.astimezone(pytz.utc)
                meeting.stop = fields.Datetime.to_string(enddate)

                startdate = fields.Datetime.from_string(meeting.start_date)
                startdate = tz.localize(startdate)  # Add "+hh:mm" timezone
                startdate = startdate.replace(hour=12)  # Set 12 AM in localtime to avoid change of date when this date is localized
                startdate = startdate.astimezone(pytz.utc)  # Convert to UTC
                meeting.start = fields.Datetime.to_string(startdate)
            else:
                meeting.write({'start': meeting.start_datetime,
                               'stop': meeting.stop_datetime})

    # -----------------------------------------------------
    @api.onchange('user_id')
    def onchange_user_id(self):
        if not self.user_id:
            return {}
        user = self.user_id
        # job=user.partner_id.function
        return {'value': {
            'directed_by_job': user.partner_id.function if user.partner_id.function else 'Cargo no definido',
        }
        }

    # --------------
    @api.onchange('objective_id')
    def onchange_objective_id(self):
        for meeting in self:
            if meeting.objective_id:
                return {'value': {'category_id': meeting.objective_id.category_id.id}}
            # else:
            #     return {'value': {'category_id': None}}

    # ---------------
    @api.onchange('category_id')
    def onchange_category_id(self):
        for meeting in self:
            if meeting.category_id:
                if meeting.objective_id and meeting.objective_id in meeting.category_id.objective_ids:
                    return {
                        'domain': {'objective_id': "[('category_id', '=', " + str(meeting.category_id.id) + ")]"},
                        'value': {'objective_id': meeting.objective_id.id}}
                else:
                    return {
                        'domain': {'objective_id': "[('category_id', '=', " + str(meeting.category_id.id) + ")]"},
                        'value': {'objective_id': None}}
            else:
                return {'domain': {},
                        'value': {'objective_id': None}
                        }

    @api.onchange('group_ids', 'individual_attendee_ids')
    def onchange_groups(self):

        if self.behave == 'assign_auto':
            lista = []
            for group in self.group_ids:
                for partner in group.partner_group_ids:
                    if partner.id not in lista:
                        lista.append(partner.id)

            for partner in self.individual_attendee_ids:
                if partner.id not in lista:
                    lista.append(partner.id)

            res = [(6, 0, lista)]

            return {'value': {'partner_ids': res, 'participants_text': self.participants_char(True)}}

    # ----------------------------------------
    # @api.model
    # def check_access_rights(self, operation, raise_exception=True):
    #     if get_uid()
    #             raise ValidationError(_('The authenticated user must be the head of at least one group or Calendar Manager.'))
    #     return super(Meeting, self).check_access_rights(operation, raise_exception)

    @api.onchange('partner_ids', 'group_task')
    def onchange_partner_ids(self):
        """" this function search automatic the partners's related groups subordinate of login user"""
        partner_ids = self.partner_ids
        group_task = self.group_task
        res = {'value': {}}

        model_config = self.env['res.groups'].fields_get()

        group_name = ''
        group_name_limited = ''
        if model_config['name']['translate']:
            group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Manager')
        else:
            group_name = _('Calendar Manager')

        if model_config['name']['translate']:
            group_name_limited = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Limited Calendar Manager')
        else:
            group_name_limited = _('Limited Calendar Manager')

        responsible_id = self.env['res.users'].browse(self._uid).partner_id.id

        calendar_manager_group = self.env['res.groups'].search([('name', '=', group_name)])
        limited_calendar_manager_group = self.env['res.groups'].search([('name', '=',group_name_limited)])

        res['value']['participants_text'] = self.participants_char(True)
        if partner_ids and group_task:
            group_list = []
            # buscar los planificadores generales configurados
            calendar_manager_users = []
            limited_calendar_manager_users = []
            for u in calendar_manager_group.users:
                calendar_manager_users.append(u.id)
            for us in limited_calendar_manager_group.users:
                limited_calendar_manager_users.append(us.id)
            if not calendar_manager_users and not limited_calendar_manager_users:
                raise ValidationError(_('You must configured at least one Calendar Manager.'))

            # Buscar de que grupo es responsable el usuario logueado
            # TODO: BUSCAR EL GRUPO DE MAYOR GERARQUIA
            responsible_group_id = self.env['l10n_cu_calendar.org_group'].search(
                [('partner_id', '=', responsible_id), ('work_plan', '=', True)])

            # si no es planificador general o planificador general limitado y no es responsable de al menos un grupo ValidationError
            if not responsible_group_id and self._uid not in calendar_manager_users and self._uid not in limited_calendar_manager_users:
                raise ValidationError(
                    _('The authenticated user must be the head of at least one group or Calendar Manager.'))
            # si el usuario es responsable de mas de un grupo con plan de trabajo se toma el primero
            for p in partner_ids:
                groups = []
                if self._uid in calendar_manager_users:
                    # si el usuario es planificador general se buscan todos los grupos
                    groups = self.env['l10n_cu_calendar.org_group'].search([('partner_group_ids', 'in', p.id),
                                                                            ('work_plan', '=', True)])
                elif self._uid in limited_calendar_manager_users:
                    # si el usuario es planificador general limitado se buscan todos los grupos
                    groups = self.env['l10n_cu_calendar.org_group'].search([('partner_group_ids', 'in', p.id),
                                                                            ('work_plan', '=', True)])
                else:
                    # si no: se buscan los grupos subordinados al grupo con plan de trabajo que es responsable
                    # si el usuario es responsable de mas de un grupo con plan de trabajo se toma el primero
                    groups = self.env['l10n_cu_calendar.org_group'].search([('partner_group_ids', 'in', p.id),
                                                                            ('work_plan', '=', True),
                                                                            ('id', 'child_of',
                                                                             responsible_group_id[0].id)])
                for g in groups:
                    if g.id not in group_list:
                        group_list.append(g.id)

            attendees_group_ids = [(6, 0, group_list)]

            res['value']['attendees_group_ids'] = attendees_group_ids
        else:
            res['value']['attendees_group_ids'] = [(6, 0, [])]

        return res
        # -------------------------------------------------

    @api.onchange('add_responsible')
    def onchange_add_responsible(self):
        for meetting in self:
            partner_ids = meetting.partner_ids
            add_responsible = meetting.add_responsible
            responsible_id = meetting.user_id.partner_id.id
            # si true adcionar el responsable
            list = []
            for p in partner_ids:
                list.append(p.id)

            if add_responsible:
                # si estaa en la lista no se adiciona
                if responsible_id in list:
                    pass
                else:
                    list.append(responsible_id)
                    # si false eliminar el responsable
            else:
                if responsible_id in list:
                    list.remove(responsible_id)
                else:
                    pass

            res = [(6, 0, list)]
            return {'value': {'partner_ids': res}
                    }

    # -------------------------------------------------
    @api.onchange('only_employee')
    def onchange_only_employee(self):
        for meetting in self:
            if meetting.only_employee:
                return {'domain': {'partner_ids': "[('employee','=',True)]", 'individual_attendee_ids': "[('employee','=',True)]"}}
            else:
                return {'domain': {'partner_ids': "[('employee','=',False)]", 'individual_attendee_ids': "[('employee','=',False)]"}}

    # ------ OVERRIDE-----
    # add user_id and mail_notification
    @api.multi
    def create_attendees(self):
        current_user = self.env.user
        result = {}
        for meeting in self:
            alreay_meeting_partners = meeting.attendee_ids.mapped('partner_id')
            meeting_attendees = self.env['calendar.attendee']
            meeting_partners = self.env['res.partner']
            for partner in meeting.partner_ids.filtered(lambda partner: partner not in alreay_meeting_partners):
                values = {
                    'partner_id': partner.id,
                    'email': partner.email,
                    'event_id': meeting.id,
                    # añadiendo el campo user_id en el attendee
                    'user_id': partner.user_ids[0].id if partner.user_ids else False,
                }

                # current user don't have to accept his own meeting
                if partner == self.env.user.partner_id:
                    values['state'] = 'accepted'

                attendee = self.env['calendar.attendee'].create(values)

                meeting_attendees |= attendee
                meeting_partners |= partner

            if meeting_attendees and meeting.mail_notification:
                to_notify = meeting_attendees.filtered(lambda a: a.email != current_user.email)
                to_notify._send_mail_to_attendees('calendar.calendar_template_meeting_invitation')

                meeting.write({'attendee_ids': [(4, meeting_attendee.id) for meeting_attendee in meeting_attendees]})
            if meeting_partners:
                meeting.message_subscribe(partner_ids=meeting_partners.ids)

            # We remove old attendees who are not in partner_ids now.
            all_partners = meeting.partner_ids
            all_partner_attendees = meeting.attendee_ids.mapped('partner_id')
            old_attendees = meeting.attendee_ids
            partners_to_remove = all_partner_attendees + meeting_partners - all_partners

            attendees_to_remove = self.env["calendar.attendee"]
            if partners_to_remove:
                attendees_to_remove = self.env["calendar.attendee"].search(
                    [('partner_id', 'in', partners_to_remove.ids), ('event_id', '=', meeting.id)])
                attendees_to_remove.unlink()

            result[meeting.id] = {
                'new_attendees': meeting_attendees,
                'old_attendees': old_attendees,
                'removed_attendees': attendees_to_remove,
                'removed_partners': partners_to_remove
            }
        return result

    @api.multi
    def _compute_access(self):
        for event in self:
            event.edit = self.check_access()

    def check_access(self):
        user = self.env['res.users'].browse(self._uid)
        partner = self.env['res.partner'].search([('id', '=', user.partner_id.id)])
        model_config = self.env['res.groups'].fields_get()

        if model_config['name']['translate']:
            group_name = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Manager')
        else:
            group_name = _('Calendar Manager')

        groups = self.env['res.groups'].search([('name', '=', group_name)])
        # print groups
        users = []
        for u in groups.users:
            users.append(u.id)

        if model_config['name']['translate']:
            group_name_limited = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Limited Calendar Manager')
        else:
            group_name_limited = _('Limited Calendar Manager')

        groups_limited = self.env['res.groups'].search([('name', '=', group_name_limited)])
        # print groups
        users_limited = []
        for u in groups_limited.users:
            users_limited.append(u.id)

        if model_config['name']['translate']:
            group_name_planif_eval = self.env['ir.translation']._get_source('', 'model', self.env.lang, 'Calendar Officer')
        else:
            group_name_planif_eval = _('Calendar Officer')

        groups_planif_eval = self.env['res.groups'].search([('name', '=', group_name_planif_eval)])
        # print groups
        users_planif_eval = []
        for u in groups_planif_eval.users:
            users_planif_eval.append(u.id)

        # If user have Calendar Manager Rol have all Rights
        if user.id in users and user.id not in users_limited:
            return True
        # If user not in Calendar Manager Rol we have to looking for user like LIMITED CALENDAR MANAGER
        elif user.id in users and user.id in users_limited:
            if self.create_uid.id == user.id:
                return True
            else:
                return False
        # If not, user should be Responsible in all event selected
        else:
            # # Voy a verificar si la persona esta tratando de poner tareas a los subordinados aunque
            # # por estructura no lo sean en el fastos
            # if user.id in users_planif_eval:
            #     valor = False
            #     # Buscar los grupos organizativos donde el responsable sea el usuario
            #     org_groups = self.env['l10n_cu_calendar.org_group'].search([('partner_id', '=', partner.id)])
            #
            #     # Buscar en el evento los participantes y verificar si son subordinados de grupo organizativo
            #     # del partner que esta accediendo a la tarea.
            #     if len(self.partner_ids) > 0:
            #         for partner_asistance in self.partner_ids:
            #             for org_g in org_groups:
            #                 if partner_asistance.id in org_g.partner_group_ids._ids:
            #                     valor = True
            #
            #     else:
            #         valor = True
            #
            #     return valor
            # else:
            for t in self:
                    if t.create_uid.id == user.id:
                        return True
                    elif user.id == 1:
                        return True
                    else:
                        # if not (t.user_id.id == user.id or not t.user_id.id):
                        return False

        return True

    # @api.model
    # def create(self, vals):
    #     if self.check_access():
    #         return super(Meeting, self).create(vals)
    #     else:
    #         raise ValidationError(_('No puede colocarle tareas a personas que no se subordinan a usted.'))
    
    @api.multi
    def write(self, values):
        if self.check_access():
            for e in self:
                if e.recurrency and 'state' in values:
                    raise ValidationError(_('You cannot change the state of a recurrent event.'))
            return super(Meeting, self).write(values)
        else:
            raise ValidationError(_('You cannot modify this event. Only event´s responsible can modify.'))

    @api.multi
    def unlink(self):
        if self.check_access():
            return super(Meeting, self).unlink()
        else:
            raise ValidationError(_('You cannot delete this event. Only event´s responsible can delete.'))

    @api.multi
    def get_ics_single_file(self):
        """ Returns iCalendar single file from a list of events.
            :returns a .ics file with all events
        """
        result = ''

        def ics_datetime(idate, allday=False):
            if idate:
                if allday:
                    return fields.Date.from_string(idate)
                else:
                    return fields.Datetime.from_string(idate).replace(tzinfo=pytz.timezone('UTC'))
            return False

        try:
            # FIXME: why isn't this in CalDAV?
            import vobject
        except ImportError:
            _logger.warning(
                "The `vobject` Python module is not installed, so iCal file generation is unavailable. Use 'pip install vobject' to install it")
            return result

        cal = vobject.iCalendar()
        for meeting in self:

            event = cal.add('vevent')

            if not meeting.start or not meeting.stop:
                raise UserError(_("First you have to specify the date of the invitation."))
            event.add('created').value = ics_datetime(time.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            event.add('dtstart').value = ics_datetime(meeting.start, meeting.allday)
            event.add('dtend').value = ics_datetime(meeting.stop, meeting.allday)
            event.add('summary').value = meeting.name
            if meeting.description:
                event.add('description').value = meeting.description
            if meeting.rrule:
                event.add('rrule').value = meeting.rrule

            if meeting.alarm_ids:
                for alarm in meeting.alarm_ids:
                    valarm = event.add('valarm')
                    interval = alarm.interval
                    duration = alarm.duration
                    trigger = valarm.add('TRIGGER')
                    trigger.params['related'] = ["START"]
                    if interval == 'days':
                        delta = timedelta(days=duration)
                    elif interval == 'hours':
                        delta = timedelta(hours=duration)
                    elif interval == 'minutes':
                        delta = timedelta(minutes=duration)
                    trigger.value = delta
                    valarm.add('DESCRIPTION').value = alarm.name or 'Odoo'
            for attendee in meeting.attendee_ids:
                attendee_add = event.add('attendee')
                attendee_add.value = 'MAILTO:' + (attendee.email or '')
            result = cal.serialize()

        return result

    @api.multi
    def detach_recurring_event(self, values=None):
        """ Detach a virtual recurring event by duplicating the original and change reccurent values
            :param values : dict of value to override on the detached event
        """
        if not values:
            values = {}

        real_id = calendar_id2real_id(self.id)
        recurrent_id_date = datetime.strftime(datetime.strptime(self.id.split('-')[1], VIRTUALID_DATETIME_FORMAT), DEFAULT_SERVER_DATETIME_FORMAT)
        meeting_origin = self.browse(real_id)
        data = self.read(['allday', 'start', 'stop', 'rrule', 'duration'])[0]
        start_temp = False
        stop_temp = False
        if not data['allday']:
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            startdate = datetime.strptime(meeting_origin['start'], DEFAULT_SERVER_DATETIME_FORMAT)
            startdate = pytz.UTC.localize(startdate)  # Add "+hh:mm" timezone
            startdate = startdate.astimezone(timezone)

            calendar_start = datetime.strptime(data['start'], DEFAULT_SERVER_DATETIME_FORMAT)
            calendar_start = pytz.UTC.localize(calendar_start)  # Add "+hh:mm" timezone
            calendar_start = calendar_start.astimezone(timezone)

            if not _is_date_time_saving(startdate) and _is_date_time_saving(calendar_start):
                calendar_stop = datetime.strptime(data['stop'], DEFAULT_SERVER_DATETIME_FORMAT)
                calendar_stop = pytz.UTC.localize(calendar_stop)  # Add "+hh:mm" timezone
                calendar_start = calendar_start.astimezone(pytz.timezone('UTC'))
                calendar_start += timedelta(hours=1)
                calendar_stop += timedelta(hours=1)
                start_temp = data['start']
                stop_temp = data['stop']
                data['start'] = datetime.strftime(calendar_start, DEFAULT_SERVER_DATETIME_FORMAT)
                data['stop'] = datetime.strftime(calendar_stop, DEFAULT_SERVER_DATETIME_FORMAT)
            elif _is_date_time_saving(startdate) and not _is_date_time_saving(calendar_start):
                calendar_stop = datetime.strptime(data['stop'], DEFAULT_SERVER_DATETIME_FORMAT)
                calendar_stop = pytz.UTC.localize(calendar_stop)  # Add "+hh:mm" timezone
                calendar_start = calendar_start.astimezone(pytz.timezone('UTC'))
                calendar_start -= timedelta(hours=1)
                calendar_stop -= timedelta(hours=1)
                start_temp = data['start']
                stop_temp = data['stop']
                data['start'] = datetime.strftime(calendar_start, DEFAULT_SERVER_DATETIME_FORMAT)
                data['stop'] = datetime.strftime(calendar_stop, DEFAULT_SERVER_DATETIME_FORMAT)

        data['start_date' if data['allday'] else 'start_datetime'] = data['start']
        data['stop_date' if data['allday'] else 'stop_datetime'] = data['stop']

        if data.get('rrule'):
            data.update(
                values,
                recurrent_id=real_id,
                recurrent_id_date=recurrent_id_date,
                rrule_type=False,
                rrule='',
                recurrency=False,
                repeat_other_year=False,
                final_date=datetime.strptime(data.get('start'), DEFAULT_SERVER_DATETIME_FORMAT if data[
                    'allday'] else DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                    hours=values.get('duration', False) or data.get('duration'))
            )

            # do not copy the id
            if data.get('id'):
                del data['id']

            return meeting_origin.copy(default=data)

    @api.multi
    def read(self, fields=None, load='_classic_read'):
        fields2 = fields and fields[:] or None
        EXTRAFIELDS = ('privacy', 'user_id', 'duration', 'allday', 'start', 'start_date', 'start_datetime', 'rrule')
        for f in EXTRAFIELDS:
            if fields and (f not in fields):
                fields2.append(f)

        select = map(lambda x: (x, calendar_id2real_id(x)), self.ids)
        real_events = self.browse([real_id for calendar_id, real_id in select])
        real_data = super(Meeting, real_events).read(fields=fields2, load=load)
        real_data = dict((d['id'], d) for d in real_data)

        result = []
        for calendar_id, real_id in select:
            res = real_data[real_id].copy()
            if res['allday'] and 'start' in res and 'stop' in res and res['start'] != res['stop']:
                start = datetime.strptime(res['start'], DEFAULT_SERVER_DATETIME_FORMAT)
                stop = datetime.strptime(res['stop'], DEFAULT_SERVER_DATETIME_FORMAT)
                duration = stop - start
                ls = calendar_id2real_id(calendar_id, with_date=duration.total_seconds() / 3600)
            else:
                ls = calendar_id2real_id(calendar_id,with_date=res and res.get('duration', 0) > 0 and res.get('duration') or 1)

            if not isinstance(ls, (basestring, int, long)) and len(ls) >= 2:
                res['start'] = ls[1]
                res['stop'] = ls[2]

                if res['allday']:
                    res['start_date'] = ls[1]
                    res['stop_date'] = ls[2]
                else:
                    timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                    startdate = datetime.strptime(real_data[real_id]['start'], DEFAULT_SERVER_DATETIME_FORMAT)
                    startdate = pytz.UTC.localize(startdate)  # Add "+hh:mm" timezone
                    startdate = startdate.astimezone(timezone)

                    calendar_start = datetime.strptime(ls[1], DEFAULT_SERVER_DATETIME_FORMAT)
                    calendar_start = pytz.UTC.localize(calendar_start)  # Add "+hh:mm" timezone
                    calendar_start = calendar_start.astimezone(timezone)

                    if not _is_date_time_saving(startdate) and _is_date_time_saving(calendar_start):
                        calendar_stop = datetime.strptime(ls[2], DEFAULT_SERVER_DATETIME_FORMAT)
                        calendar_stop = pytz.UTC.localize(calendar_stop)  # Add "+hh:mm" timezone
                        calendar_start = calendar_start.astimezone(pytz.timezone('UTC'))
                        calendar_start -= timedelta(hours=1)
                        calendar_stop -= timedelta(hours=1)
                        res['start_datetime'] = datetime.strftime(calendar_start, DEFAULT_SERVER_DATETIME_FORMAT)
                        res['start'] = res['start_datetime']
                        res['stop_datetime'] = datetime.strftime(calendar_stop, DEFAULT_SERVER_DATETIME_FORMAT)
                        res['stop'] = res['stop_datetime']
                    elif _is_date_time_saving(startdate) and not _is_date_time_saving(calendar_start):
                        calendar_stop = datetime.strptime(ls[2], DEFAULT_SERVER_DATETIME_FORMAT)
                        calendar_stop = pytz.UTC.localize(calendar_stop)  # Add "+hh:mm" timezone
                        calendar_start = calendar_start.astimezone(pytz.timezone('UTC'))
                        calendar_start += timedelta(hours=1)
                        calendar_stop += timedelta(hours=1)
                        res['start_datetime'] = datetime.strftime(calendar_start, DEFAULT_SERVER_DATETIME_FORMAT)
                        res['start'] = res['start_datetime']
                        res['stop_datetime'] = datetime.strftime(calendar_stop, DEFAULT_SERVER_DATETIME_FORMAT)
                        res['stop'] = res['stop_datetime']
                    else:
                        res['start_datetime'] = ls[1]
                        res['stop_datetime'] = ls[2]

                if 'display_time' in fields:
                    res['display_time'] = self._get_display_time(ls[1], ls[2], res['duration'], res['allday'])

            res['id'] = calendar_id
            result.append(res)

        for r in result:
            if r['user_id']:
                user_id = type(r['user_id']) in (tuple, list) and r['user_id'][0] or r['user_id']
                partner_id = self.env.user.partner_id.id
                if user_id == self.env.user.id or partner_id in r.get("partner_ids", []):
                    continue
            if r['privacy'] == 'private':
                for f in r.keys():
                    recurrent_fields = self._get_recurrent_fields()
                    public_fields = list(set(
                        recurrent_fields + ['id', 'allday', 'start', 'stop', 'display_start', 'display_stop',
                                            'duration', 'user_id', 'state', 'interval', 'count', 'recurrent_id_date',
                                            'rrule']))
                    if f not in public_fields:
                        if isinstance(r[f], list):
                            r[f] = []
                        else:
                            r[f] = False
                    if f == 'name':
                        r[f] = _('Busy')

        for r in result:
            for k in EXTRAFIELDS:
                if (k in r) and (fields and (k not in fields)):
                    del r[k]
        return result

    @api.multi
    def task_done_all(self):
        if self.check_access() and self.attendee_ids:
            self.attendee_ids.task_done()
        return True

    @api.multi
    def task_not_done_all(self):
        if self.check_access() and self.attendee_ids:
            self.attendee_ids.task_not_done()
        return True

    @api.multi
    def action_detach_and_confirm_event(self):
        meeting = self.detach_recurring_event()
        meeting.write({'state': 'open'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'res_id': meeting.id,
            'target': 'current',
            'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}}
        }

    @api.constrains('partner_ids')
    def _validate_partner_ids(self):
        if self.partner_ids and not self.add_anyway:
            ocuppied_members = ''
            flag_partner = False
            if self.allday:
                date_start = self.start_date + ' 00:00:00'
                date_end = self.stop_date + ' 23:59:59'
            else:
                tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
                date_start_aux = fields.Datetime.from_string(self.start_datetime)
                date_start = tz.localize(date_start_aux).astimezone(pytz.utc)
                date_start = fields.Datetime.to_string(date_start)
                date_end_aux = fields.Datetime.from_string(self.stop_datetime)
                date_end = tz.localize(date_start_aux).astimezone(pytz.utc)
                date_end = fields.Datetime.to_string(date_end)

                # timezone = pytz.timezone(self._context.get('tz') or 'UTC')
                # startdate = datetime.strptime(self.start_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                # startdate = pytz.UTC.localize(startdate)  # Add "+hh:mm" timezone
                # startdate = startdate.astimezone(timezone)
                #
                # date_start = fields.Datetime.to_string(startdate)
                #
                # stopdate = datetime.strptime(self.stop_datetime, DEFAULT_SERVER_DATETIME_FORMAT)
                # stopdate = pytz.UTC.localize(stopdate)  # Add "+hh:mm" timezone
                # stopdate = stopdate.astimezone(timezone)
                #
                # date_end = fields.Datetime.to_string(stopdate)

            for partner in self.partner_ids:
                flag = False
                domain_search = [('start', '<=', date_end), ('stop', '>=', date_end)]
                if isinstance(self.id, int):
                    domain_search.append(('id', '!=', self.id))
                meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                if len(meetings_object) > 0:
                    ids_object = []
                    for ids in meetings_object:
                        if partner.id in ids.partner_ids._ids:
                            if ids.id not in ids_object:
                                ids_object.append(ids.id)
                            flag = True
                            flag_partner = True

                    if flag:
                        ocuppied_members += partner.name + ', '

                if not flag:
                    domain_search = [('start', '<=', date_start), ('stop', '>=', date_start)]
                    if isinstance(self.id, int):
                        domain_search.append(('id', '!=', self.id))
                    meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                    if len(meetings_object) > 0:
                        ids_object = []
                        for ids in meetings_object:
                            if partner.id in ids.partner_ids._ids:
                                if ids.id not in ids_object:
                                    ids_object.append(ids.id)
                                flag = True
                                flag_partner = True

                        if flag:
                            ocuppied_members += partner.name + ', '

                if not flag:
                    domain_search = [('start', '>=', date_start), ('stop', '<=', date_end)]
                    if isinstance(self.id, int):
                        domain_search.append(('id', '!=', self.id))
                    meetings_object = self.env['calendar.event'].with_context(mymeetings=False).search(domain_search)

                    if len(meetings_object) > 0:
                        ids_object = []
                        for ids in meetings_object:
                            if partner.id in ids.partner_ids._ids:
                                if ids.id not in ids_object:
                                    ids_object.append(ids.id)
                                flag = True
                                flag_partner = True

                        if flag:
                            ocuppied_members += partner.name + ', '

            if flag_partner:
                raise ValidationError(_("El/los empleado(s) " + ocuppied_members + "ya tienen una actividad programada "
                                                                             "en el mismo horario. Debe verificar el campo "
                                                                             "'Coincidencia programada' para planificar la "
                                                                             "tarea de todos modos."))

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default.update({'state': 'draft'})
        context = dict(self._context)
        return super(models.Model, self.browse(calendar_id2real_id(self.id)).with_context(context)).copy(default)

    @api.model
    def send_message_day_act_unfulfilled(self):
        # Enviar mensaje al planificador evaluador para que recuerde abrir el periodo
        # Server date begin
        # from_zone = tz.tzutc()
        # to_zone = tz.tzlocal()
        # utc = datetime.datetime.strptime(datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), '%Y-%m-%d %H:%M:%S')
        # utc = utc.replace(tzinfo=from_zone)
        # central = utc.astimezone(to_zone)
        # central.strftime("%Y-%m-%d")
        # Server date end
        # Verificar que dia de la semana es el 5 del mes en curso. Si cae sabado se le resta un dia y si
        # cae domingo se le restan 2.
        # tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc
        now_date = fields.Date.from_string(fields.Date.today())
        # A peticion de Addiel deben mostrarse las tareas del dia siguiente. Febrero 2020
        tomorrow_date = now_date + relativedelta(days=1)
        tomorrow_date_string = fields.Date.to_string(tomorrow_date)
        # date_str_begin = fields.Date.today() + ' 00:00:00'
        # date_str_end = fields.Date.today() + ' 21:50:59'
        # date_str = self.invert_date(fields.Date.today())
        date_str_begin = tomorrow_date_string + ' 00:00:00'
        date_str_end = tomorrow_date_string + ' 21:50:59'
        date_str = self.invert_date(tomorrow_date_string)
        # now_fecha = fields.Datetime.now().
        # Buscar los calendar event que se deben realizar en el dia y enviar un mensaje con el id para cada
        # uno de ellos darles cumplimiento.
        tz = pytz.timezone(self.env.user.tz) if self.env.user.tz else pytz.utc

        # Solucion del write modificada
        events = self.search([('start', '>=', date_str_begin), ('start', '<=', date_str_end)])
        mail_thread = self.env['mail.message']
        for ev in events:
            timezone = pytz.timezone(self._context.get('tz') or 'UTC')
            date = fields.Datetime.from_string(ev.start)
            startdate = date.replace(tzinfo=pytz.timezone('UTC')).astimezone(timezone)
            start = startdate.strftime("%d/%m/%Y %I:%M:%S")
            hour = startdate.strftime("%I:%M")
            # old solution
            # take the user timezone
            timezone_old = pytz.timezone(self._context.get('tz') or 'UTC')
            startdate_old = pytz.UTC.localize(fields.Datetime.from_string(ev.start))  # Add "+hh:mm" timezone
            # Convert the start date to saved timezone (or context tz) as it'll
            # define the correct hour/day asked by the user to repeat for recurrence.
            start_old = startdate.astimezone(timezone)  # transform "+hh:mm" timezone
            start_old = fields.Datetime.to_string(start_old)  # convert to string

            # start = fields.Datetime.from_string(ev.start)
            # date_event = tz.localize(start)
            # date_event = date_event.replace(hour=8)  # Set 8 AM in localtime
            # date_event = date_event.astimezone(pytz.utc)  # Convert to UTC
            # meeting.start = fields.Datetime.to_string(startdate)
            # date_event = fields.Datetime.from_string(startdate)

            date_event = start
            # hour = date_event.strftime("%I:%M")
            if startdate.hour > 12:
                hour = hour + ' pm'
            elif startdate.hour <= 12:
                hour = hour + ' am'
            else:
                hour = 'T/D'

            # Looking for attendees
            attendee = self.env['calendar.attendee'].search([('event_id', '=', ev.id)])
            # Looking for the partner using user_id field
            for att in attendee:
                if ev.fulfilled == False:
                    short_name = 'No tiene nombre corto'
                    if ev.short_name:
                        short_name = ev.short_name
                    values_message = {'subject': 'PLAN DE TRABAJO ' + date_str + ' - ' + hour + ' - ' + short_name,
                                      'message_type': 'notification',
                                      'partner_ids': [[6, False, [att.partner_id.id]]],
                                      'body': (('<html>%s</html>') % ev.name),
                                      'model': 'calendar.event',
                                      'record_name': date_str + ' - ' + hour + ' - ' + short_name,
                                      'author_id': 464,
                                      'res_id': ev.id
                                      }
                    message_internal = mail_thread.sudo().create(values_message)

        return True


class RegistryInformation(models.TransientModel):
    _name = "l10n_cu_calendar.registry_information"

    def _get_seed(self):
        return self.env['l10n_cu_base.reg'].get_seed('l10n_cu_calendar')

    def _get_key(self):
        return self.env['l10n_cu_base.reg'].get_key('l10n_cu_calendar')

    def _get_days(self):
        return self.env['l10n_cu_base.reg'].get_days('l10n_cu_calendar')

    def _get_reg(self):
        status = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_calendar')
        if status in ('invalidkey', 'invalidmod'):
            return 'unreg'
        if status == 'expkey':
            return 'exp'
        if status == 'nokey':
            return 'sinclave'
        if status == 'ok':
            return 'reg'

    seed = fields.Char('Seed', readonly=True, default=_get_seed)
    key = fields.Char('Key', default=_get_key)
    state = fields.Selection([('unreg', 'Unregistered'), ('reg', 'Registered'), ('exp', 'Expired'),('sinclave', 'Sin clave')], default=_get_reg,
                             string='UEB Desoft', )
    days_left = fields.Integer('Days left', default=_get_days, readonly=True)

    # days_percent=

    def save_key(self):
        return self.env['l10n_cu_base.reg'].save_key('l10n_cu_calendar', self.key)
