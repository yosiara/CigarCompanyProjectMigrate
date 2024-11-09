# -*- coding: utf-8 -*-

from odoo import api
from odoo.models import Model
from odoo.fields import Integer, Char, Boolean


class VersatConcept(Model):
    _name = 'versat.concept'
    _description = 'versat.concept'

    idconcepto = Integer()
    idregdocum = Integer()
    idcriterio = Integer()
    codigo = Integer()
    description = Char()
    idcategoria = Integer()
    activo = Boolean()
    to_import = Boolean(string='Import?')
    is_out_operation = Boolean(string='Is out operation?')

    @api.multi
    def write(self, vals):
        res = super(VersatConcept, self).write(vals)
        return res
VersatConcept()
