# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _default_archive_nro(self):
        sequence = self.env['ir.sequence'].search([('code', '=', 'partner.archive.number')])
        return sequence.get_next_char(sequence.number_next_actual)


    contract_count = fields.Integer(compute='_compute_contract_count', string='# of Contract')
    contract_ids = fields.One2many('sale.order', 'partner_id', 'Sales Order')
    contract_number_sequence_id = fields.Many2one('ir.sequence', 'Contract Sequence', ondelete='restrict')
    archive_nro = fields.Char('Archive Nro', default=_default_archive_nro)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.reeup_code:
                name = record.reeup_code + '/' + name
            elif record.ci:
                name = record.ci + '/' + name
            else:
                name = record.name
            res.append((record.id, name))
        return res

    def _compute_contract_count(self):
        contract_data = self.env['l10n_cu_contract.contract'].read_group(domain=[('partner_id', 'child_of', self.ids)],
                                                      fields=['partner_id'], groupby=['partner_id'])
        # read to keep the child/parent relation while aggregating the read_group result in the loop
        partner_child_ids = self.read(['child_ids'])
        mapped_data = dict([(m['partner_id'][0], m['partner_id_count']) for m in contract_data])
        for partner in self:
            # let's obtain the partner id and all its child ids from the read up there
            partner_ids = filter(lambda r: r['id'] == partner.id, partner_child_ids)[0]
            partner_ids = [partner_ids.get('id')] + partner_ids.get('child_ids')
            # then we can sum for all the partner's child
            partner.contract_count = sum(mapped_data.get(child, 0) for child in partner_ids)

    @api.model
    def create(self, vals_list):
        res = super(ResPartner, self).create(vals_list)
        res.create_contract_sequence()
        archive_nro = self.env['ir.sequence'].next_by_code('partner.archive.number') or '/'
        res.write({'archive_nro': archive_nro})
        return res

    def create_contract_sequence(self):
        """
        This method creates ir.sequence fot the current contract
        :return: Returns create sequence
        """
        self.ensure_one()
        sequence_data = self._prepare_contract_sequence_data()
        sequence = self.env["ir.sequence"].sudo().create(sequence_data)
        self.write({"contract_number_sequence_id": sequence.id})
        return sequence

    def _prepare_contract_sequence_data(self, init=True):
        """
        This method prepares data for create/update_sequence methods
        :param init: Set to False in case you don't want to set initial values
        for number_increment and number_next_actual
        """
        values = {
            "name": "{} {}".format(_("Contract number sequence for partner"), self.name),
            "implementation": "standard",
            "code": "partner.contract.number.{}".format(self.id),
            "padding": 3,
            "use_date_range": False,
        }
        if init:
            values.update(dict(number_increment=1, number_next_actual=1))
        return values

    def get_next_contract_number(self):
        sequence_id = self.sudo().contract_number_sequence_id
        if not sequence_id:
            sequence_id = self.create_contract_sequence()
        return sequence_id.next_by_id()




