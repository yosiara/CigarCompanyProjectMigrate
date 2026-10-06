import logging
from collections import defaultdict

from odoo import models, _

_logger = logging.getLogger(__name__)

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    # -------------------------------------------------------------------------
    # OVERRIDE METHODS
    # -------------------------------------------------------------------------
    def write(self, vals):
        unarchiving = vals.get('active') is True
        changing_job = 'job_id' in vals
        changing_stage = 'stage_id' in vals

        if not (unarchiving or changing_job or changing_stage):
            return super().write(vals)

        if changing_stage:
            if vals['stage_id']:
                new_stage_hired = self.env['hr.recruitment.stage'].browse(vals['stage_id']).hired_stage
            else:
                new_stage_hired = False
        else:
            new_stage_hired = None  # None = "sin cambio"

        job_counts = defaultdict(int)
        for app in self:
            # Estado final tras el write.
            final_active = vals.get('active', app.active)
            final_job_id = vals['job_id'] if changing_job else app.job_id.id
            final_hired = new_stage_hired if changing_stage else app.stage_id.hired_stage

            # ¿Consumía plaza antes del write?
            old_consumed = app.active and app.stage_id.hired_stage and not app.employee_id

            # ¿Consumirá plaza después del write?
            new_consumed = final_active and final_hired and not app.employee_id

            # Solo valida si va a consumir plaza o migró a un job distinto.
            if not new_consumed:
                continue
            if old_consumed and final_job_id == app.job_id.id:
                continue
            if final_job_id:
                job_counts[final_job_id] += 1

        for job_id, count in job_counts.items():
            self.env['hr.job'].browse(job_id)._check_vacant_position(additional=count)

        return super().write(vals)

    # def create_employee_from_applicant(self):
    #     self.ensure_one()
    #     self = self.with_context(from_applicant_hire=True)
    #     return super(HrApplicant, self).create_employee_from_applicant()