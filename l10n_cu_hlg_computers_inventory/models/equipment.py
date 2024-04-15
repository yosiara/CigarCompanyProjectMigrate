# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import mm
import base64
from odoo.tools.translate import _
from odoo.exceptions import ValidationError


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    employee_ids = fields.Many2many('hr.employee', 'maintenance_equipment_resp_employees_rel', 'equipment_id', 'employee_id', 'Employees')
    equipment_assign_to = fields.Selection(selection_add=[('employees', 'Employees')], ondelete= {'employees': 'set default'})
    inventory_number = fields.Char('Inventory Number')
    seal = fields.Char('Seal')
    ocs_external_id = fields.Integer(index=True)
    component_ids = fields.One2many('equipment.component', 'equipment_id', 'Component', readonly=True)
    is_a_computer = fields.Boolean('Is an ICT equipment?', default=False)
    cycle_id = fields.Integer()

    # Administrative data...
    user_name = fields.Char()
    operative_system = fields.Char()
    os_version = fields.Char()

    uuid = fields.Char()
    architecture = fields.Char()

    domain = fields.Char()
    ip_address = fields.Char()
    information_updated_date = fields.Datetime()

    # To know the state in the importation...
    # 1 -> Imported.
    # 2 -> Updated first time.
    # 3 -> Updated more than once time.
    importation_state = fields.Selection([('1', '1'), ('2', '2'), ('3', '3')], default='1')

    local_id = fields.Many2one('l10n_cu_locals.local', 'Used in local')

    component_ids = fields.One2many(
        'equipment.component', 'equipment_id', 'Component', domain=[('is_active', '=', True)]
    )

    software_ids = fields.One2many('equipment.software', 'equipment_id', 'Software')

    qrcode_image = fields.Binary("QRCode", compute='get_qrimage')

    @api.onchange('equipment_assign_to')
    def _onchange_equipment_assign_to(self):
        if self.equipment_assign_to == 'employee':
            self.department_id = False
        if self.equipment_assign_to == 'department':
            self.employee_id = False
        if self.equipment_assign_to == 'employees':
            self.employee_id = False
            self.department_id = False
        self.assign_date = fields.Date.context_today(self)

    ##@api.one
    @api.depends('employee_id', 'department_id', 'equipment_assign_to')
    def _compute_owner(self):
        self.owner_user_id = self.env.user.id
        if self.equipment_assign_to == 'employee':
            self.owner_user_id = self.employee_id.user_id.id
        elif self.equipment_assign_to == 'department':
            self.owner_user_id = self.department_id.manager_id.user_id.id
        elif self.equipment_assign_to == 'employees':
            self.owner_user_id = self.employee_ids[0].user_id.id

    @api.model
    def create(self, vals):
        equipment = super(MaintenanceEquipment, self).create(vals)
        # subscribe employees when equipment assign to them.
        user_ids = []
        for employee in equipment.employee_ids:
            if employee.user_id:
                user_ids.append(employee.user_id.id)
        if user_ids:
            equipment.message_subscribe_users(user_ids=user_ids)
        return equipment

    ##@api.multi
    def write(self, vals):
        res = super(MaintenanceEquipment, self).write(vals)
        user_ids = []
        # subscribe employees when equipment assign to them.
        if vals.get('employee_ids'):
            for employee in self.employee_ids:
                if employee.user_id:
                    user_ids.append(employee.user_id.id)
        if user_ids:
            self.message_subscribe_users(user_ids=user_ids)
        return res

    ##@api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'employee_ids' in init_values and self.employee_ids:
            return 'maintenance.mt_mat_assign'
        return super(MaintenanceEquipment, self)._track_subtype(init_values)

    ##@api.one
    @api.depends('name', 'equipment_assign_to', 'employee_id', 'department_id', 'local_id', 'inventory_number')
    def get_qrimage(self):
        options = {'width': 100 * mm, 'height': 100 * mm}
        name = self.name if self.name else ''
        assign_to = (self.employee_id.name if self.employee_id else '') + (', ' if self.department_id and self.employee_id else '') + (self.department_id.name if self.department_id else '')

        qr_code = _('Name: %s\n') % name
        qr_code += _('Assign To: %s\n') % assign_to
        qr_code += _('Local: %s\n') % (self.local_id.name if self.local_id else '')
        qr_code += _('Inventory Number: %s\n') % (self.inventory_number if self.inventory_number else '')
        ret_val = createBarcodeDrawing('QR', value=tools.ustr(qr_code), **options)
        self.qrcode_image = base64.encodestring(ret_val.asString('jpg'))

    ##@api.one
    def confirm_all(self):
        self.software_ids.write({'ocs_external_id': False})
        return True

    ##@api.one
    def del_not_confirmed(self):
        self.env['equipment.software'].search([('equipment_id', '=', self.id), ('ocs_external_id', '!=', False),
                                               ('ocs_external_id', '!=', 0)]).unlink()
        return True

    ##@api.one
    def update_from_ocs(self):
        connector = self.env['db_external_connector.template'].search([('application', '=', 'ocs_inventory')], limit=1)
        if connector:
            self.env['equipment.software'].search([('equipment_id', '=', self.id), ('ocs_external_id', '!=', False),
                                                   ('ocs_external_id', '!=', 0)]).unlink()
            obj = self.env['computers_inventory.import_computers_wizard'].create({'connector_id': connector.id})
            connection = obj.connector_id.connect()
            obj._update_software_information(connection, self)
            connection.close()
        else:
            raise ValidationError(_('You must configure an ocs inventory connection in order to use this functionality.'))
        return True


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    def _get_default_team_id(self):
        return self.env.ref('maintenance.equipment_team_maintenance', raise_if_not_found=False)

    @api.model
    def _domain_equipment_id(self):
        domain = []
        if self._context.get('is_a_tic_request_action', False):
            domain.append(('is_a_computer', '=', True))
        return domain

    maintenance_type = fields.Selection(selection_add=[('upgrade', 'Upgrade')])
    maintenance_team_type = fields.Boolean('External Maintenance Team?')
    external_maintenance_team = fields.Char('External Maintenance Team')
    maintenance_team_id = fields.Many2one('maintenance.team', string='Team', required=False, default=_get_default_team_id)
    is_a_tic_request = fields.Boolean('ICT maintenance request', default=False)
    equipment_id = fields.Many2one(domain=_domain_equipment_id)
    ict_maintenance_order_ids = fields.One2many('computers_inventory.work_order', 'maintenance_request_id', 'ICT work orders')

    @api.constrains('is_a_tic_request')
    def _constrain_is_a_tic_request(self):
        if self.is_a_tic_request and not self.equipment_id.is_a_computer:
            raise ValidationError(_('The equipment associated to this maintenance request should be an information technology equipment.'))

    @api.model
    def create(self, vals):
        if self._context.get('is_a_tic_request_action', False):
            vals['is_a_tic_request'] = True
        res = super(MaintenanceRequest, self).create(vals)
        return res

    @api.onchange('employee_id', 'department_id')
    def onchange_department_or_employee_id(self):
        return {'domain': {}}

    def create_order(self):
        if self.id:
            return {
                'name': _('Create Work Order'),
                'type': 'ir.actions.act_window',
                'res_model': 'computers_inventory.create_order_wzd',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': dict(self._context),
            }



