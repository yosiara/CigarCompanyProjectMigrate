# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

TERM = [
    (1, 'One'),
    (2, 'Two'),
    (3, 'Three'),
    (4, 'Four'),
    (5, 'Five'),
    (6, 'Six'),
    (7, 'Seven'),
    (8, 'Eight'),
    (9, 'Nine'),
    (10, 'Ten'),
]

resp_dic = {'nokey': _('You must request a registry key. Please contact the suport center for a new one.'),
            'invalidkey': _('You are using a invalid key. Please contact the suport center for a new one.'),
            'expkey': _('You are using a expired key. Please contact the suport center for a new one.')}


class ContractType(models.Model):
    _name = "l10n_cu_contract.contract_type"
    _inherit = ['mail.thread']

    name = fields.Char('Name', required=True, help='Contracts for the provision of services', copy=False)
    color = fields.Integer('Color')
    active = fields.Boolean('Active', required=True, default=True)
    sequence_id = fields.Many2one('ir.sequence', 'Sequence',
                                  help='If it is defined it automatically generates the numbers of the associated contracts')
    parent_consecutive = fields.Boolean('Number consecutive for parent', default=False,
                                        help='If it is activated it defined automatically generates the numbers of the associated contracts for principal')
    flow = fields.Selection([
        ('customer', 'Sale'),
        ('supplier', 'Purchase'),
    ], 'Flow', required=True)
    format = fields.Selection([
        ('verb', 'Verb'),
        ('write', 'Write'),
    ], 'Format', required=True, default='write',
        help='If the format is written, the template for the printing of the contracts must be defined',
        track_visibility='always')

    # Report ------------------------------------------------------------------------------
    template_data = fields.Binary("Template", track_visibility='always')
    filename = fields.Char('File Name')
    ir_actions_report_xml_id = fields.Many2one('ir.actions.report.xml', 'Report')
    # ---------------------------------------------------------------------------------------

    term = fields.Selection(TERM, 'Term (Years)', required=True,
                            help='Term in years of validity for contracts related to the type of contract',
                            track_visibility='always')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    # TODO:Parent
    required_parent = fields.Boolean('Required Parent', default=False,
                                     help='If activated it shows you the types of contracts which can be the parent of this to select it',
                                     track_visibility='always')
    parent_id = fields.Many2one('l10n_cu_contract.contract_type', 'Parent Contract Type',
                                index=True,
                                help='Possible types of parent contracts for this type of contract',
                                track_visibility='always')
    child_id = fields.One2many('l10n_cu_contract.contract_type', 'parent_id', 'Child Contract')
    # TODO:Judgment
    required_judgment = fields.Boolean('Required Judgment',
                                       help='If activated it can be assigned to contracts legal opinions',
                                       track_visibility='always')
    # TODO:Lines
    required_lines = fields.Boolean('Required Lines',
                                    help='If activated it can be assigned to the contract lines of details of products or services',
                                    track_visibility='always')
    # TODO:Payment
    required_milestone_payment = fields.Boolean('Required Milestone Payment',
                                                help='If activated it can be assigned to contracts milestones of payments',
                                                track_visibility='always')
    # TODO:Check
    check_lines = fields.Boolean('Check Details Lines (Invoice)', compute='_compute_check_lines', store=True,
                                 help='Check that only the lines of contracted products or services are on the invoices',
                                 track_visibility='always')
    check_quantity_lines = fields.Boolean('Check Quantity Lines (Invoice)', default=False,
                                          help='Check that only the contracted quantities are executed on invoices',
                                          track_visibility='always')
    check_general_amount = fields.Boolean('Check Amount Lines (Invoice)', default=False,
                                          help='Verify that only the total contracted amount is executed in invoices',
                                          track_visibility='always')
    # TODO: Compute field
    count_contract_draft = fields.Integer(compute='_compute_contract_count')
    count_contract_in_process = fields.Integer(compute='_compute_contract_count')
    count_contract_in_progress = fields.Integer(compute='_compute_contract_count')

    contract_type_sequence_id = fields.Many2one('ir.sequence', 'Contract Type Sequence', ondelete='restrict')

    _constraints = [(models.BaseModel._check_recursion,
                     'Circular references are not permitted between contract and sub-contract', ['parent_id'])]

    @api.multi
    def copy(self, default=None):
        raise UserError(_("No puede duplicar los tipos de contratos!"))

    @api.multi
    def _get_action(self, action_xmlid):
        # TDE TODO check to have one view + custo in methods
        action = self.env.ref(action_xmlid).read()[0]
        if self:
            action['display_name'] = self.display_name
        return action

    @api.multi
    def get_contract_action_contract_type(self):
        return self._get_action('l10n_cu_hlg_contract.contract_action_contract_type')

    @api.multi
    def get_contract_action_contract_type_draft(self):
        return self._get_action('l10n_cu_hlg_contract.contract_action_contract_type_draft')

    @api.multi
    def get_contract_action_contract_type_process(self):
        return self._get_action('l10n_cu_hlg_contract.contract_action_contract_type_process')

    @api.multi
    def get_contract_action_contract_type_progress(self):
        return self._get_action('l10n_cu_hlg_contract.contract_action_contract_type_progress')

    @api.multi
    def _compute_contract_count(self):
        domains = {
            'count_contract_draft': [('state', '=', 'draft')],
            'count_contract_in_process': [('state', 'in', ['pending_dict', 'pending_appro',
                                                           'rejected', 'approval',
                                                           'pending_signed'])],
            'count_contract_in_progress': [('state', 'in', ['open'])],
        }
        for field in domains:
            data = self.env['l10n_cu_contract.contract'].read_group(domains[field] +
                                                                    [('contract_type', 'in', self.ids)],
                                                                    ['contract_type'], ['contract_type'])
            count = dict(
                map(lambda x: (x['contract_type'] and x['contract_type'][0], x['contract_type_count']), data))
            for record in self:
                record[field] = count.get(record.id, 0)

    @api.onchange('required_milestone_payment')
    def _onchange_required_milestone_payment(self):
        if self.required_milestone_payment:
            self.required_lines = True

    @api.one
    @api.depends('check_quantity_lines')
    def _compute_boolean(self):
        if self.check_quantity_lines:
            self.check_lines = True
        else:
            self.check_lines = False

    @api.one
    @api.depends('check_quantity_lines')
    def _compute_check_lines(self):
        if self.check_quantity_lines:
            self.check_lines = True
            self.check_quantity_lines = True
            self.check_general_amount = True
        else:
            self.check_lines = False
            self.check_quantity_lines = False
            self.check_general_amount = False

    @api.onchange('required_lines')
    def _onchange_required_lines(self):
        if self.required_lines:
            self.check_lines = True
            self.check_quantity_lines = True
        else:
            self.check_lines = False
            self.check_quantity_lines = False
            self.check_general_amount = False

    @api.model
    def create(self, vals):
        contract_type = super(ContractType, self).create(vals)
        docxtpl_template = self.env['docxtpl.template'].sudo().create({'name': contract_type.name,
                                                          'docxtpl_template_data': contract_type.template_data})
        docxtpl_report = self.env['ir.actions.report.xml'].create({'name': contract_type.name,
                                                                'model': 'l10n_cu_contract.contract',
                                                                'report_type': 'docxtpl',
                                                                'report_name': contract_type.name,
                                                                'docxtpl_filetype': 'docx',
                                                                'docxtpl_template_id':docxtpl_template.id,
                                                                'module': 'l10n_cu_report_docxtpl'})
        contract_type.write({'ir_actions_report_xml_id': docxtpl_report.id})
        contract_type.create_contract_type_sequence()
        return contract_type

    @api.multi
    def write(self, vals):
        if 'template_data' in vals and vals['template_data'] is False:
            for obj in self:
                obj.ir_actions_report_xml_id.docxtpl_template_id.unlink()
        if vals.get('template_data'):
            for obj in self:
                if not obj.ir_actions_report_xml_id:
                    docxtpl_template = self.env['docxtpl.template'].create({'name': obj.name,
                                                                      'docxtpl_template_data': vals['template_data']})
                    docxtpl_report = self.env['ir.actions.report.xml'].create({'name': obj.name,
                                                                            'model': 'l10n_cu_contract.contract',
                                                                            'report_type': 'docxtpl',
                                                                            'report_name': obj.name,
                                                                            'docxtpl_filetype': 'docx',
                                                                            'docxtpl_template_id': docxtpl_template.id,
                                                                            'module': 'l10n_cu_report_docxtpl'})

                    obj.ir_actions_report_xml_id = docxtpl_report.id
                elif not obj.ir_actions_report_xml_id.docxtpl_template_id:
                    docxtpl_template = self.env['docxtpl.template'].create({'name': obj.name,
                                                                      'docxtpl_template_data': vals['template_data']})
                    obj.ir_actions_report_xml_id.docxtpl_template_id = docxtpl_template.id
                else:
                    obj.ir_actions_report_xml_id.docxtpl_template_id.write(
                        {'docxtpl_template_data': vals['template_data']})
        return super(ContractType, self).write(vals)

    @api.multi
    def unlink(self):
        for obj in self:
            if len(self.env['l10n_cu_contract.contract'].search([('contract_type', '=', obj.id)])) > 0:
                raise ValidationError(_('No puede eliminar tipo de contrato con contratos asociados.'))
            obj.ir_actions_report_xml_id.docxtpl_template_id.sudo().unlink()
            self.env['docxtpl.report'].sudo().search(
                [('ir_actions_report_xml_id', '=', obj.ir_actions_report_xml_id.id)]).unlink()
            obj.ir_actions_report_xml_id.sudo().unlink()
        return super(ContractType, self).unlink()

    @api.one
    @api.constrains('name')
    def check_reg(self):
        resp = self.env['l10n_cu_base.reg'].check_reg('l10n_cu_contract')
        if resp != 'ok':
            raise ValidationError(resp_dic[resp])

    def create_contract_type_sequence(self):
        """
        This method creates ir.sequence fot the current contract type
        :return: Returns create sequence
        """
        self.ensure_one()
        sequence_data = self._prepare_contract_type_sequence_data()
        sequence = self.env["ir.sequence"].sudo().create(sequence_data)
        self.write({"contract_type_sequence_id": sequence.id})
        return sequence

    def _prepare_contract_type_sequence_data(self, init=True):
        """
        This method prepares data for create/update_sequence methods
        :param init: Set to False in case you don't want to set initial values
        for number_increment and number_next_actual
        """
        values = {
            "name": "{} {}".format(_("Contract number sequence for type contract"), self.name),
            "implementation": "standard",
            "code": "contract.type.number.{}".format(self.id),
            "suffix": "/%(year)s",
            "padding": 3,
            "use_date_range": False,
        }
        if init:
            values.update(dict(number_increment=1, number_next_actual=1))
        return values

    def get_next_contract_type_number(self):
        sequence_id = self.sudo().contract_type_sequence_id
        if not sequence_id:
            sequence_id = self.create_contract_type_sequence()
        return sequence_id.next_by_id()