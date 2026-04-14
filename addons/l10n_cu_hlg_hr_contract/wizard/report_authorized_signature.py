# -*- coding: utf-8 -*-
#
#

from openerp import fields
from openerp import models, api
import time
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from datetime import datetime, timedelta, date

class ContractReportWizard(models.TransientModel):
	_name = 'l10n_cu_hlg_hr_contract.report_wizard'

	contract_id = fields.Many2one('hr.contract',string="Contract")
	company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
	authorized_signature_id = fields.Many2one('l10n_cu_base.authorized_signature','Authorized signature',domain=[('model','=','hr.contract')],required=True)
	emp_authorized_signature_id = fields.Many2one('hr.employee',string="Authorized Employee", required=True)

	@api.onchange('authorized_signature_id','company_id')
	def onchange_authorized_signature(self):
		emp_aut_sig_ids = []
		if self.authorized_signature_id:
			for emp in self.authorized_signature_id.employee_ids:
				emp_aut_sig_ids.append(emp.id)
		domain = "[('id','in'," + str(emp_aut_sig_ids) + ")]"
		return {'domain': {'emp_authorized_signature_id': domain}}

	def check_report(self):
		if self.contract_id.clasification == 'framework':
			data = {'emp_aut_sig_id': self.emp_authorized_signature_id.id,'docids':[self.contract_id.id]}
			if self.contract_id.contract_type == 'indeterminate':
				return self.env['report'].get_action([], 'l10n_cu_hlg_hr_contract.report_indeterminate_contract',data=data)
			if self.contract_id.contract_type == 'determinate':
				return self.env['report'].get_action([], 'l10n_cu_hlg_hr_contract.report_determinate_contract',data=data)
		else: raise ValidationError(_('The selected contract is not a framework contract'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
