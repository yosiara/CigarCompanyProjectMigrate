# -*- coding: utf-8 -*-

from odoo import models, fields


class SmokeConcept(models.Model):
    _name = "smoke.concept"
    _description = "Smoke Concepts"

    name = fields.Char(string="Name", required=True)
