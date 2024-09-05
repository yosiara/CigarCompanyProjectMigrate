# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Smoke(models.Model):
    _name = "smoke"

    _description = "main model of smoke"

    name = fields.Char(
        string="nombre",
    )
