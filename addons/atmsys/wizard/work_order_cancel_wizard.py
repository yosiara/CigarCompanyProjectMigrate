# -*- coding: utf-8 -*-
from datetime import datetime

from odoo.fields import Selection, Binary, Char
from odoo.models import TransientModel
from odoo.tools import ustr


class WorkOrderCancelWizard(TransientModel):
    _name = 'atmsys.work_order_cancel_wizard'
    _description = 'atmsys.work_order_cancel_wizard'

    description = Char('Motivo de Cancelación')


    def action_cancel(self):
        active_id = self.env.context.get('active_id', False)
        if active_id:
            work_order_id = self.env['atmsys.work_order'].search([('id', '=', active_id)])
            work_order_id.write({
                'description_cancel': self.description,
                'user_cancel_id': self.env.user.id,
                'date_cancel': datetime.now(),
                'state': 'cancel'

            })

WorkOrderCancelWizard()
