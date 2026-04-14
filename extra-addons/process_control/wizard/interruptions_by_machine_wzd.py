# -*- coding: utf-8 -*-


from odoo import models, fields, api


class WzdInterruptionsByMachine(models.TransientModel):
    _name = 'process_control.interruptions_machine_wzd'

    start_date = fields.Date('Desde', required=True)
    end_date = fields.Date('Hasta', required=True)
    machine = fields.Many2one(comodel_name="process_control.machine", string="Máquina", required=False, )
    machine_type_id = fields.Many2one('process_control.machine_type', string='Tipo de máquina',
                                      related='machine.machine_type_id')
    subset = fields.Many2one(comodel_name="process_control.machine_set_of_peaces",
                             string="Subconjunto", required=False, domain="[('machine_type_id', '=', machine)]")
    interruption_type = fields.Many2one('process_control.interruption_type', 'Tipo')

    def print_report(self):
        return self.env['report'].get_action(self, 'process_control.interruptions_by_machine_report', data={
            'start_date': self.start_date,
            'end_date': self.end_date,
            'machine': self.machine.id,
            'subset': self.subset.id,
            'interruption_type': self.interruption_type.id,
        })
