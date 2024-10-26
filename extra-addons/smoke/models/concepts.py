# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SmokeConcepts(models.Model):
    _name = "smoke.concepts"

    _description = "Smoke Concepts"

    name = fields.Char(string="Name")

    date = fields.Date(
        string="Date",
        default=fields.Date.context_today,
    )
