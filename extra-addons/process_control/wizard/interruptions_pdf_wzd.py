# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InterruptionsPdfReportWzd(models.TransientModel):
    _name = "process_control.interruptions_pdf_report_wzd"
    _description = "Interruptions pdf report wzd"

    start_date = fields.Date('Desde *', required=True)
    end_date = fields.Date('Hasta *', required=True)
    interruption_type_id = fields.Many2one('process_control.interruption_type', 'Tipo')
    
    productive_section_id = fields.Many2one(comodel_name="process_control.productive_section", string="Módulo", ondelete='cascade')
    productive_line_id = fields.Many2one('process_control.productive_line', string='Línea')
    
    machine_id = fields.Many2one('process_control.machine', string='Máquina')
    machine_domain = fields.Binary(compute="_get_machine_domain", exportable=False)
    
    set_of_peaces_id = fields.Many2one("process_control.machine_set_of_peaces", string="Subconjunto de Piezas")
    peaces_domain = fields.Binary(compute="_get_peaces_domain", exportable=False)

    filt = fields.Selection([
        ('productive_section', 'Módulo'),
        ('productive_line', 'Línea'),
        ('machine', 'Máquina'),
    ], string='Filtrado por *', default="productive_section")

    @api.depends("machine_id")
    def _get_peaces_domain(self):
        for rec in self:
            rec.peaces_domain = [('id', 'in', rec.machine_id.set_of_peaces.ids)] if rec.machine_id else []

    @api.depends("interruption_type_id")
    def _get_machine_domain(self):
        for rec in self:
            if rec.interruption_type_id and rec.interruption_type_id.machine_type_related:
                rec.machine_domain = [('machine_type_id', 'in', rec.interruption_type_id.machine_type_related.ids)]
            else:
                rec.machine_domain = []

    @api.onchange("interruption_type_id")
    def _onchange_machine_id(self):
        if self.interruption_type_id.machine_type_related and self.machine_id.machine_type_id.id not in self.interruption_type_id.machine_type_related.ids:
            self.machine_id = False

    def print_report(self):
        self.ensure_one()
        if self.end_date < self.start_date:
            raise ValidationError(_("The start date cannot be greater than the end date"))
        data = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "interruption_type_id": self.interruption_type_id.id,
            "productive_section_id": self.productive_section_id.id if self.filt == "productive_section" else False,
            "productive_line_id": self.productive_line_id.id if self.filt == "productive_line" else False,
            "machine_id": self.machine_id.id if self.filt == "machine" else False,
            "set_of_peaces_id": self.set_of_peaces_id.id if self.filt == "machine" else False,
            "filt": self.filt,
        }
        return self.env.ref("process_control.interruptions_pdf_report_action").report_action(self, data=data)

    # _name = 'process_control.interruptions_machine_wzd'
    # start_date = fields.Date('Desde', required=True)
    # end_date = fields.Date('Hasta', required=True)
    # machine = fields.Many2one(comodel_name="process_control.machine", string="Máquina", required=False, )
    # machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina',
    #                                   related='machine.machine_type_id')
    # subset = fields.Many2one(comodel_name="process_control.machine_set_of_peaces",
    #                          string="Subconjunto", required=False, domain="[('machine_type_id', '=', machine)]")
    # interruption_type = fields.Many2one('process_control.interruption_type', 'Tipo')

    # def print_report(self):
    #     return self.env['report'].get_action(self, 'process_control.interruptions_by_machine_report', data={
    #         'start_date': self.start_date,
    #         'end_date': self.end_date,
    #         'machine': self.machine.id,
    #         'subset': self.subset.id,
    #         'interruption_type': self.interruption_type.id,
    #     })

    #     _name = 'process_control.interruptions_line_wzd'

    # start_date = fields.Date('Desde', required=True)
    # end_date = fields.Date('Hasta', required=True)
    # interruption_type = fields.Many2one('process_control.interruption_type', 'Tipo')
    # productive_line = fields.Many2one(comodel_name="process_control.productive_line",
    #                                      string="Línea productiva", ondelete='cascade')

    # def print_report(self):
    #     return self.env['report'].get_action(self, 'process_control.interruptions_by_line_report', data={
    #         'start_date': self.start_date,
    #         'end_date': self.end_date,
    #         'productive_line': self.productive_line.id,
    #         'interruption_type': self.interruption_type.id,
    #     })