# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class InterruptionsPdfReportWzd(models.TransientModel):
    _name = "process_control.interruptions_pdf_report_wzd"
    _description = "Interruptions pdf report wzd"

    start_date = fields.Date('Desde *', required=True)
    end_date = fields.Date('Hasta *', required=True)
    interruption_type_ids = fields.Many2many('process_control.interruption_type', string='Interruption Type',
                            relation="interruptions_pdf_report_wzd_interruption_type_asoc", column1='interruptions_pdf_report_wzd_id', column2='interruption_type_id'
    )
    productive_section_ids = fields.Many2many('process_control.productive_section', string='Módulo',
                            relation="interruptions_pdf_report_wzd_productive_section_asoc", column1='interruptions_pdf_report_wzd_id', column2='productive_section_id'
    )
    productive_line_ids = fields.Many2many('process_control.productive_line', string='Línea',
                            relation="interruptions_pdf_report_wzd_productive_line_asoc", column1='interruptions_pdf_report_wzd_id', column2='productive_line_id'
    )
    machine_ids = fields.Many2many('process_control.machine', string='Máquina',
                            relation="interruptions_pdf_report_wzd_machine_asoc", column1='interruptions_pdf_report_wzd_id', column2='machine_id'
    )
    machine_domain = fields.Binary(compute="_get_machine_domain", exportable=False)
    
    set_of_peaces_ids = fields.Many2many('process_control.machine_set_of_peaces', string='Subconjunto de Piezas',
                            relation="interruptions_pdf_report_wzd_machine_set_of_peaces_asoc", column1='interruptions_pdf_report_wzd_id', column2='machine_set_of_peaces_id'
    )
    peaces_domain = fields.Binary(compute="_get_peaces_domain", exportable=False)

    filt = fields.Selection([
        ('productive_section', 'Módulo'),
        ('productive_line', 'Línea'),
        ('machine', 'Máquina'),
    ], string='Filtrado por *', default="productive_section")

    @api.depends("machine_ids")
    def _get_peaces_domain(self):
        for rec in self:
            rec.peaces_domain = [('id', 'in', rec.machine_ids.set_of_peaces.ids)] if rec.machine_ids else []

    @api.depends("interruption_type_ids")
    def _get_machine_domain(self):
        for rec in self:
            if rec.interruption_type_ids and rec.interruption_type_ids.machine_type_related:
                rec.machine_domain = [('machine_type_id', 'in', rec.interruption_type_ids.machine_type_related.ids)]
            else:
                rec.machine_domain = []

    @api.onchange("interruption_type_ids")
    def _onchange_machine_id(self):
        if self.interruption_type_ids.machine_type_related:
            ids = [m.id for m in self.machine_ids if m.machine_type_id.id not in self.interruption_type_ids.machine_type_related.ids]
            self.machine_ids = self.machine_ids.filtered(lambda m: m.id not in ids)

    def print_report(self):
        self.ensure_one()
        if self.end_date < self.start_date:
            raise ValidationError(_("The start date cannot be greater than the end date"))
        data = {
            "start_date": self.start_date,
            "end_date": self.end_date,
            "interruption_type_ids": self.interruption_type_ids.ids,
            "productive_section_ids": self.productive_section_ids.ids if self.filt == "productive_section" else False,
            "productive_line_ids": self.productive_line_ids.ids if self.filt == "productive_line" else False,
            "machine_ids": self.machine_ids.ids if self.filt == "machine" else False,
            "set_of_peaces_ids": self.set_of_peaces_ids.ids if self.filt == "machine" else False,
            "filt": self.filt,
        }
        return self.env.ref("process_control.interruptions_pdf_report_action").report_action(self, data=data)