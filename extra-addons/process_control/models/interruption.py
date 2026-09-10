# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

class Interruption(models.Model):
    _name = 'process_control.interruption'
    _description = 'Interruption'

    start_date = fields.Float(string='Start Date *', required=True)
    end_date = fields.Float(string='End Date *', required=True)
    
    interruption_type_id = fields.Many2one('process_control.interruption_type', 'Type *', required=True, default=lambda self: self.interruption_type_id.search([('code', '=', 'PM')], limit=1))
    interruption_type_domain = fields.Binary(compute='_get_interruption_type_domain', exportable=False)

    machine_id = fields.Many2one('process_control.machine', 'Machine')
    machine_domain = fields.Binary(compute='_get_machine_domain', exportable=False)
    
    set_of_peaces_id = fields.Many2one('process_control.machine_set_of_peaces', 'Set of Peaces')
    peaces_domain = fields.Binary(compute='_get_peaces_domain', exportable=False)
    
    productive_line_id = fields.Many2one('process_control.productive_line', 'Productive Line')
    line_domain = fields.Binary(compute='_get_line_domain', exportable=False)

    tech_control_id = fields.Many2one('process_control.tech_control', 'Tech Control *', ondelete='cascade', required=True)
    

    # -------------------------------------------------------------------------
    # CONSTRAINS METHODS
    # -------------------------------------------------------------------------

    @api.constrains('start_date', 'end_date')
    def _constrains_date_range(self):
        for rec in self:
            if rec.start_date >= rec.end_date:
                raise ValidationError(_('The start date %s must be earlier than the end date %s.') % (rec.start_date, rec.end_date))
            hour_range = rec.tech_control_id.turn_id.hour_range(session=rec.tech_control_id.session)
            if rec.start_date < hour_range[0] or rec.end_date > hour_range[1]:
                raise ValidationError(_('The start and/or end time of the interruption is not within the range of the selected session.'))
    
    # -------------------------------------------------------------------------
    # COMPUTE METHODS
    # -------------------------------------------------------------------------

    @api.depends('tech_control_id', 'productive_line_id')
    def _get_machine_domain(self):
        for rec in self:
            if rec.productive_line_id:
                rec.machine_domain = [('productive_line_id', '=', rec.productive_line_id.id)]
            elif rec.tech_control_id.productive_section_id:
                rec.machine_domain = [('productive_section_id', '=', rec.tech_control_id.productive_section_id.id), ('productive_line_id', '=', False)]
            else:
                rec.machine_domain = [('id', 'in', [])]

    @api.depends('machine_id')
    def _get_peaces_domain(self):
        for rec in self:
            rec.peaces_domain = [('id', 'in', rec.machine_id.set_of_peaces.ids)] if rec.machine_id else [('id', 'in', [])]

    @api.depends('tech_control_id')
    def _get_line_domain(self):
        for rec in self:
            if rec.tech_control_id.productive_section_id:
                rec.line_domain = [('productive_section_id', '=', rec.tech_control_id.productive_section_id.id)]
            else:
                rec.line_domain = [('id', 'in', [])]

    @api.depends('machine_id')
    def _get_interruption_type_domain(self):
        for rec in self:
            if rec.machine_id:
                rec._cr.execute(f"SELECT interruption_type_id FROM process_control_interruption_type_machine_type_asoc WHERE machine_type_id='{rec.machine_id.machine_type_id.id}'")
                ids_asoc = [i[0] for i in rec._cr.fetchall()]
                rec.interruption_type_domain = ['|', ('machine_type_related', '=', False), ('id', 'in', ids_asoc), ('activate', '=', True)]
            else:
                rec.interruption_type_domain = [('machine_type_related', '=', False), ('activate', '=', True)]

    # -------------------------------------------------------------------------
    # ONCHANGE METHODS
    # -------------------------------------------------------------------------

    @api.onchange('productive_line_id')
    def _onchange_productive_line_id(self):
        if self.productive_line_id.id is not self.machine_id.productive_line_id.id:
            self.machine_id = False

    @api.onchange('machine_id')
    def _onchange_machine_id(self):
        if self.set_of_peaces_id.id not in self.machine_id.set_of_peaces.ids:
            self.set_of_peaces_id = False
        if self.interruption_type_id.machine_type_related and self.machine_id.machine_type_id.id not in self.interruption_type_id.machine_type_related.ids:
            self.interruption_type_id = False

    @api.onchange('tech_control_id')
    def _onchange_tech_control_id(self):
        hour_range = self.tech_control_id.turn_id.hour_range(session=self.tech_control_id.session)
        self.start_date = hour_range[0]
        self.end_date = hour_range[1]

    # @api.model_create_multi
    # @api.depends('interruption_type', 'machine_id')
    # def _calc_name(self):
    #     for intp in self:
    #         if intp.interruption_type.name and intp.machine_id.name:
    #             intp.name = tools.ustr(intp.interruption_type.name) + '-' + tools.ustr(intp.machine_id.name)
    #         elif intp.interruption_type.name and not intp.machine_id.name:
    #             intp.name = tools.ustr(intp.interruption_type.name)
    #         elif not intp.interruption_type.name and intp.machine_id.name:
    #             intp.name = tools.ustr(intp.machine_id.name)