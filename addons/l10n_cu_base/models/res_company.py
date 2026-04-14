# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re

class ResCompany(models.Model):
    _inherit = 'res.company'

    @api.constrains('website')
    def _check_website(self):
        url = re.compile(r"^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$")
        if not url.search(self.website):
            raise ValidationError("Error! La URL no es correct.")

    @api.constrains('email')
    def _check_email(self):
        url = re.compile(r"[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,6}")
        if not url.search(self.email):
            raise ValidationError(u"Error! El correo electrónico no es correcto.")

    @api.constrains('phone')
    def _check_phone(self):
        if len(str(self.phone)) < 8:
            raise ValidationError(u"Error! El teléfono debe tener más de 8 dígitos.")

