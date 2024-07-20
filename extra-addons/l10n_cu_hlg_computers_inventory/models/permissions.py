# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import timedelta, datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PermissionsSoftwareModule(models.Model):
    _name = 'computers_inventory.permissions_software_module'
    _description = 'permissions_software_module'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)


class SoftwareModule(models.Model):
    _name = 'computers_inventory.software_module'
    _description = 'software_module'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    permissions_module_ids = fields.Many2many('computers_inventory.permissions_software_module',
                                              relation='computers_inventory_software_module_permission_rel',
                                              string='Permissions')
    software_id = fields.Many2one('computers_inventory.software', 'Software', required=True)


class Software(models.Model):
    _name = 'computers_inventory.software'
    _description = 'software'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    version = fields.Char(string='Version')
    os = fields.Selection([('windows', 'Windows'), ('linux', 'Linux'), ('unix', 'Unix'),
                           ('mac_OS', 'MacOS')], string='OS')
    installation_mode = fields.Char(string='Installation mode', help='Ejemplo: .exe, .deb')
    manufacturer = fields.Char(string='Manufacturer')
    orientation = fields.Many2one('computers_inventory.nomenclator_orientation', 'Orientation')
    is_modular = fields.Boolean('Is modular?')
    module_ids = fields.One2many('computers_inventory.software_module', 'software_id', 'Modules')
    state = fields.Selection([('draft', 'Draft'), ('requested', 'Requested'), ('approved', 'Approved'),
                              ('obsolete', 'Obsolete')],
                             'Status', track_visibility='onchange', default='draft')

    #@api.one
    def action_requested(self):
        self.state = 'requested'

    #@api.one
    def action_approved(self):
        self.state = 'approved'

    #@api.one
    def action_obsolete(self):
        self.state = 'obsolete'


class SoftwareLines(models.Model):
    _name = 'computers_inventory.software_lines'
    _description = 'software_lines'
    _rec_name = 'software_id'

    software_id = fields.Many2one('computers_inventory.software', 'Software', required=True)
    authorized_software_id = fields.Many2one('computers_inventory.authorized_software', 'Authorized Software')
    version = fields.Char(string='Version', related='software_id.version', readonly='True')
    valid = fields.Date(string='Valid')
    module_id = fields.Many2one('computers_inventory.software_module', 'Module')
    permissions_ids = fields.Many2many('computers_inventory.permissions_software_module',
                                       'computers_inventory_permissions_software_lines_rel',
                                       'software_line_id', 'permissions_id', 'Permissions')

    @api.onchange('software_id')
    def onchange_software(self):
        if self.software_id:
            return {'domain': {'module_id': [('software_id', '=', self.software_id.id)]}, 'value': {'module_id': False}}
        return {}

    @api.onchange('module_id')
    def onchange_module(self):
        if self.module_id:
            return {'domain': {'permissions_ids': [('id', 'in', self.module_id.permissions_module_ids.ids)]},
                    'value': {'permissions_ids': False}}
        return {}


class AuthorizedSoftware(models.Model):
    _name = 'computers_inventory.authorized_software'
    _description = 'authorized_software'

    #@api.one
    def _compute_name(self):
        if self.id:
            self.name = _('Software solicitude #%s') % self.id

    name = fields.Char('Name', compute=_compute_name)
    everyone = fields.Boolean('Everyone', default=True)
    resource_ids = fields.Many2many('maintenance.equipment', 'computers_inventory_equipment_authorized_software_rel',
                                    'authorized_software_id', 'resource_id', 'Resources')
    applicant_id = fields.Many2one('hr.employee', 'Applicant', required=True)
    department_id = fields.Many2one('hr.department', 'Department', required=True)
    date = fields.Date(string='Date')
    objective = fields.Text(string='Objectives')
    software_line_ids = fields.One2many('computers_inventory.software_lines', 'authorized_software_id',
                                        'Software lines')
    approve_by_id = fields.Many2one('hr.employee', 'Approve')
    state = fields.Selection([('new', 'New'), ('requested', 'Requested'), ('approved', 'Approved'),
                              ('rejected', 'Rejected'), ('executed', 'Executed')], 'Status', default='new')

    #@api.one
    def action_requested(self):
        self.state = 'requested'

    #@api.one
    def action_approved(self):
        self.state = 'approved'
        approve = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if approve:
            self.approve_by_id = approve.id

    #@api.one
    def action_rejected(self):
        self.state = 'rejected'

    #@api.one
    def action_executed(self):
        self.state = 'executed'

    @api.onchange('applicant_id')
    def _onchange_applicant_id(self):
        if self.applicant_id and self.applicant_id.department_id:
            return {'value': {'department_id': self.applicant_id.department_id.id}}
        else:
            return {'value': {'department_id': False}}


class NomenclatorOrientation(models.Model):
    _name = 'computers_inventory.nomenclator_orientation'
    _description = 'nomenclator_orientation'
    _rec_name = 'orientation'

    orientation = fields.Char(string='Orientation', required=True)


class SecureDeletion(models.Model):
    _name = 'computers_inventory.secure_deletion'
    _description = 'secure_deletion'
    _inherit = 'computers_inventory.send_mail_mixin'
    _rec_name = 'resource_id'

    external = fields.Boolean('External', default=True)
    capacity = fields.Integer('Capacity', help='La capacidad tiene que ser un número entero')
    resource_id = fields.Many2one('maintenance.equipment', 'Resource')
    executor_id = fields.Many2one('hr.employee', 'Executor', related='resource_id.employee_id', required=True)
    department_id = fields.Many2one('hr.department', 'Department', related='resource_id.department_id')
    erasing_tool = fields.Char('Erasing tool')
    observations = fields.Text('Observations')
    state = fields.Selection([('new', 'New'), ('requested', 'Requested'), ('approved', 'Approved'),
                              ('executed', 'Executed')],
                             'Status', track_visibility='onchange', default='new')

    #@api.one
    def action_requested(self):
        self.state = 'requested'
        recipients = self.get_computer_inventory_responsible()
        if self.executor_id and self.executor_id.user_id and self.executor_id.user_id.email:
            recipients.append(self.executor_id.user_id.email)
        recipients = list(set(recipients))
        self.send_mail('l10n_cu_hlg_computers_inventory.computer_inventory_template_secure_deletion', force_send=False,
                       recipients=recipients)

    #@api.one
    def action_approved(self):
        self.state = 'approved'

    #@api.one
    def action_executed(self):
        self.state = 'executed'
        recipients = self.get_computer_inventory_responsible()
        if self.executor_id and self.executor_id.user_id and self.executor_id.user_id.email:
            recipients.append(self.executor_id.user_id.email)
        recipients = list(set(recipients))
        self.send_mail('l10n_cu_hlg_computers_inventory.computer_inventory_template_secure_deletion_executed', force_send=False,
                       recipients=recipients)


class PlanningSaves(models.Model):
    _name = 'computers_inventory.planning_saves'
    _description = 'planning_saves'

    name = fields.Char('Name', compute='_compute_name')
    department_id = fields.Many2one('hr.department', 'Department', required=True)
    planned_date = fields.Date('Planned Date')
    file_size = fields.Integer('File size')
    responsible_id = fields.Many2one('hr.employee', 'Responsible', required=True)
    place = fields.Char('Place')
    frequency = fields.Integer('Frequency')
    support = fields.Char('Support')
    information = fields.Char('Information')

    #@api.one
    @api.depends('department_id', 'planned_date')
    def _compute_name(self):
        if self.planned_date and self.department_id:
            self.name = '%s(%s)' % (self.department_id.name, self.planned_date)


class NetworkLicense(models.Model):
    _name = 'computers_inventory.network_license'
    _description = 'network_license'

    name = fields.Char('Name')
    date = fields.Date('Date')
    validity = fields.Integer('Validity')
    days_left = fields.Integer('Days left', compute='_compute_days_left')
    image = fields.Binary('Image')
    responsible_ids = fields.Many2many('hr.employee', 'computers_inventory_employee_network_license_rel',
                                       'network_license_id',
                                       'employee_id', 'Responsible', required=True)

    #@api.one
    @api.depends('date', 'validity')
    def _compute_days_left(self):
        if self.date:
            date_start = datetime.strptime(self.date, '%Y-%m-%d')
            today = datetime.today()
            days = (today - date_start).days
            self.days_left = self.validity - days


class TelematicsService(models.Model):
    _name = 'computers_inventory.telematics_service'

    name = fields.Char('Name', required=True)


class TelematicsServiceLines(models.Model):
    _name = 'computers_inventory.telematics_service_lines'
    _description = 'TelematicsServiceLines'

    service_id = fields.Many2one('computers_inventory.telematics_service', 'Service', required=True)
    justification = fields.Text('Justification')
    system_application_id = fields.Many2one('computers_inventory.system_service_application',
                                            'System/Service application', required=True)


class SystemsLines(models.Model):
    _name = 'computers_inventory.systems_lines'
    _description = 'systems_lines'

    software_id = fields.Many2one('computers_inventory.software', 'Software', required=True)
    module_id = fields.Many2one('computers_inventory.software_module', 'Module')
    permissions_ids = fields.Many2many('computers_inventory.permissions_software_module',
                                       'computers_inventory_permissions_systems_lines_rel',
                                       'systems_lines_id', 'permissions_id', 'Permissions')
    justification = fields.Text('Justification')
    system_application_id = fields.Many2one('computers_inventory.system_service_application',
                                            'System/Service application', required=True)

    @api.onchange('software_id')
    def onchange_software(self):
        if self.software_id:
            return {'domain': {'module_id': [('software_id', '=', self.software_id.id)]}, 'value': {'module_id': False}}
        return {}

    @api.onchange('module_id')
    def onchange_module(self):
        if self.module_id:
            return {'domain': {'permissions_ids': [('id', 'in', self.module_id.permissions_module_ids.ids)]},
                    'value': {'permissions_ids': False}}
        return {}


class SystemServiceApplication(models.Model):
    _name = 'computers_inventory.system_service_application'
    _description = 'SystemServiceApplication'
    _inherit = 'computers_inventory.send_mail_mixin'

    def _compute_name(self):
        for record in self:
            if record.id:
                record.name = _('System/Service Application #%s') % record.id

    name = fields.Char('Name', compute=_compute_name)
    date = fields.Date('Date', required=True,
                       default=lambda self: datetime.today().strftime(DEFAULT_SERVER_DATE_FORMAT))
    type = fields.Selection([('auth', 'Authorization'), ('cancel', 'Cancelation')], 'Type', required=True,
                            default='auth')
    applicant_id = fields.Many2one('hr.employee', 'Applicant', required=True)
    benefited_id = fields.Many2one('hr.employee', 'Benefited', required=True)
    approve_by_id = fields.Many2one('hr.employee', 'Approve')
    state = fields.Selection(
        [('new', 'New'), ('requested', 'Requested'), ('approved', 'Approved'), ('executed', 'Executed')], 'State',
        default='new')
    system_line_ids = fields.One2many('computers_inventory.systems_lines', 'system_application_id', 'Systems')
    service_line_ids = fields.One2many('computers_inventory.telematics_service_lines', 'system_application_id',
                                       'Telematics services')

    @api.model
    def system_string(self):
        flag = False
        result = ''
        for system in self.system_line_ids:
            if flag:
                result += ', '
            result += system.software_id.name
        return result

    @api.model
    def services_string(self):
        flag = False
        result = ''
        for system in self.service_line_ids:
            if flag:
                result += ', '
            result += system.service_id.name
        return result

    #@api.one
    def action_requested(self):
        self.state = 'requested'
        recipients = self.get_computer_inventory_responsible()
        recipients = list(set(recipients))
        self.send_mail('l10n_cu_hlg_computers_inventory.computer_inventory_template_system_service_request',
                       force_send=False, recipients=recipients)

    #@api.one
    def action_approved(self):
        self.state = 'approved'
        approve = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        if approve:
            self.approve_by_id = approve.id

    #@api.one
    def action_executed(self):
        self.state = 'executed'
