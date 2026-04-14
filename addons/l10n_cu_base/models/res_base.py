# -*- coding: utf-8 -*-

from odoo import api, fields, models, modules
from odoo.exceptions import ValidationError
from datetime import datetime, date, timedelta
from odoo.tools.translate import _
import uuid
import base64, os
import hashlib
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AuthorizedSignature(models.Model):
    _name = 'l10n_cu_base.authorized_signature'
    _rec_name = 'model'

    model = fields.Many2one('ir.model', 'Model')
    employee_ids = fields.Many2many('hr.employee', string='Authorized')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class Reg(models.Model):
    _name = 'l10n_cu_base.reg'
    _order = 'code'

    name = fields.Char('Name', size=64, required=True)
    code = fields.Char('key', )
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env['res.company']._company_default_get())

    def get_seed(self, m):
        d = date.today()
        h = hashlib.md5()
        h.update(m)
        h = h.hexdigest()
        seed = str(uuid.getnode()) + '@' + d.strftime("%d%m%Y") + '@' + h
        encoded = base64.b64encode(seed)
        return encoded

    def get_key(self, m):
        keys = self.env['l10n_cu_base.reg'].search([('name', '=', m)])
        if keys:
            for k in keys:
                return k.code
        else:
            return ''

    def get_days(self, m):
        days_left = 0
        key = self.get_key(m)
        if key:
            try:
                todayd = date.today()
                decoded_key = base64.b64decode(key)
                date_end = str(decoded_key).split('@')[0]
                date_end = datetime.strptime(date_end, "%d%m%Y")
                days_left = date_end.date() - todayd
                days_left = days_left.days
            except:
                print 'Some error occurs during key validation. Please contact the suport center for a new one.'

        return days_left

    def check_reg(self, m):
        """ check registry            
            :param m: name of module
            :return: possible error with registry or ok
        """
        key = self.get_key(m)
        #return 'ok'

        if not key:
            module = self.env['l10n_cu_base.reg'].search([('name', '=', m)])
            if not module.create_date:
                return 'nokey'
            rest = datetime.today() - datetime.strptime(module.create_date, "%Y-%m-%d %H:%M:%S")
            if rest.days < 10:
                var_str = 'Tiempo de prueba. Restante: ' + str(10 - rest.days) + ' dias'
                self.env.user.notify_warning(var_str)
                return 'ok'
            return 'nokey'

        identifier = ''
        decoded_key = ''
        try:
            decoded_key = base64.b64decode(key)
            identifier = str(decoded_key).split('@')[1]
        except:
            return 'invalidkey'
        if identifier != str(uuid.getnode()):
            return 'invalidkey'
        lst = str(decoded_key).split('@')
        if len(lst) < 3:
            return 'invalidkey'
        date_end = str(decoded_key).split('@')[0]
        date_end = datetime.strptime(date_end, "%d%m%Y")
        today = datetime.today()
        if date_end <= today:
            return 'expkey'
        mod = str(decoded_key).split('@')[2]
        h = hashlib.md5()
        h.update(m)
        h = h.hexdigest()
        if h != mod:
            return 'invalidmod'
        return 'ok'

    def save_key(self, m, k):
        try:
            # TODO: HACER LAS MISMAS VALIDACIONES DE LA FUNC check_reg
            try:
                decoded_key = base64.b64decode(str(k))
                identifier = str(decoded_key).split('@')[1]
            except:
                raise ValidationError(_('You are using a invalid key. Please contact the suport center for a new one.'))

            if identifier != str(uuid.getnode()):
                raise ValidationError(_('You are using a invalid key. Please contact the suport center for a new one.'))

            date_end = str(decoded_key).split('@')[0]
            date_end = datetime.strptime(date_end, "%d%m%Y")
            today = datetime.today()
            if date_end <= today:
                raise ValidationError(_('You are using a expired key. Please contact the suport center for a new one.'))

            ids = self.search([('name', '=', m)])
            if len(ids) == 0:
                self.create({'name': m, 'code': k})
            else:
                ids.write({'code': k})
            return True
        except:
            raise ValidationError(
                _(u'Algunos errores ocurrieron durante la validación. Por favor contacte al centro de soporte por una clave vlida.'))
