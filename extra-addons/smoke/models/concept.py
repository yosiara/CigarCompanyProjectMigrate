# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SmokeConcept(models.Model):
    _name = "smoke.concept"

    _description = "Smoke Concepts"

    #    date = fields.Date(string="Date", required=True)

    name = fields.Char(string="Concept", required=True)

    # external_concept_id = fields.Integer(
    #     string="Integration with idconcepto in Versat db", required=True
    # )
