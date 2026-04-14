# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, tools, _
from datetime import timedelta, datetime, date

class ArticleToRetiredType(models.Model):
    _name = 'turei_retired_person.article_to_retired_type'

    code = fields.Char('Code', size=60, required=True)
    name = fields.Char('Name', size=120, required=True)

class ArticleToRetired(models.Model):
    _name = 'turei_retired_person.article_to_retired'

    article_to_retired_type_id = fields.Many2one('turei_retired_person.article_to_retired_type',string='Article Type')
    name = fields.Char('Name', size=120, required=True)








