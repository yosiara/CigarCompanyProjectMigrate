# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class DBExternalConnector(models.Model):
    _inherit = "db_external_connector.template"

    application = fields.Selection(
        selection_add=[('sgp', 'Sistema de Gestión de la Producción')],
    )