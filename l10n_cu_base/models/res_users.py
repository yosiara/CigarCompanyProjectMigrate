# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
import re


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.constrains('email')
    def _check_email(self):
        url = re.compile(r"[\w.%+-]+@[\w.-]+\.[a-zA-Z]{2,6}")
        if not url.search(self.email):
            raise ValidationError(u"Error! El correo electrónico no es correcto.")

