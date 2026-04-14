# -*- coding: utf-8 -*-

import logging
import time

import odoo
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


def str2tuple(s):
    return safe_eval('tuple(%s)' % (s or ''))


class IrCron(models.Model):
    _inherit = "ir.cron"

    connector_id = fields.Many2one('db_external_connector.template', 'DB External Connector')

    @api.multi
    def method_direct_trigger(self):
        for cron in self:
            if cron.connector_id:
                self.sudo(user=cron.user_id.id).with_context(connector_id=cron.connector_id)._callback(cron.model, cron.function,
                                                                                     cron.args, cron.id)
            else:
                self.sudo(user=cron.user_id.id)._callback(cron.model, cron.function, cron.args, cron.id)

        return True