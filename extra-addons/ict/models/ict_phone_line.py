# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class IctPhoneLine(models.Model):
    _name = 'ict.phone.line'
    _description = 'ICT Phone Line'
    _rec_name = 'phone_number'

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='ict.employee',
        ondelete='restrict',
        tracking=True,
    )

    phone_number = fields.Char(
        string='Phone Number',
        required=True,
        index=True,
        help='Phone number of the line'
    )
    imsi = fields.Char(
        string='IMSI',
        help='International Mobile Subscriber Identity'
    )
    sim_card = fields.Char(
        string='SIM Card',
        help='SIM card serial number (ICCID)'
    )
    pin = fields.Char(
        string='PIN',
        size=4,
        help='SIM card PIN code'
    )
    puk = fields.Char(
        string='PUK',
        size=8,
        help='SIM card PUK unlock code'
    )
    secondary_language = fields.Char(
        string='Secondary Language',
        help='Secondary language configured on the line'
    )
    written_language = fields.Char(
        string='Written Language',
        help='Preferred written language'
    )
    sms_cap_plan = fields.Char(
        string='SMS Cap Plan',
        help='Contracted SMS cap plan'
    )
    calls_cap_plan = fields.Char(
        string='Calls Cap Plan',
        help='Contracted calls cap plan'
    )
    roaming_cap_plan = fields.Char(
        string='Roaming Cap Plan',
        help='Contracted roaming cap plan'
    )
    gprs_cap_plan = fields.Char(
        string='GPRS Cap Plan',
        help='Contracted GPRS data cap plan'
    )
    sms_package = fields.Char(
        string='SMS Package',
        help='Included SMS package (e.g. "100 SMS")'
    )
    plan_rate = fields.Char(
        string='Plan/Rate',
        help='Main tariff plan name'
    )
    gprs_package = fields.Char(
        string='GPRS Package',
        help='Contracted GPRS data package (e.g. "1GB")'
    )
    gprs_profile = fields.Char(
        string='GPRS Profile',
        help='GPRS/APN connection profile'
    )
    serv = fields.Char(
        string='SERV.',
        help='Services'
    )


