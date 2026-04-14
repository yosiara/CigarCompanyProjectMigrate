# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class DocxTplTemplate(models.Model):
    _name = 'docxtpl.template'

    name = fields.Char(required=True)
    docxtpl_template_data = fields.Binary("Template")
    filetype = fields.Selection(
        selection=[
            ('docx', "DOCX Text Document")
        ],
        string="Template File Type",
        required=True,
        default='docx')
