# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, tools, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_resource
from odoo.tools.translate import _


class HrTureiExternalArea(models.Model):
    _name = 'hr_turei.external_area'

    _sql_constraints = [
        ('name_company_uniq', 'unique (name, company_id)', 'The name of the area must be unique per company!'),
    ]

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    name = fields.Char('Name', required=True)
    carries_daily_smoking = fields.Boolean('Carries Daily Smoking', required=True)
    external_staff_ids = fields.One2many('hr_turei.external_staff', 'area_id', 'Associated')
    smoking_type = fields.Selection([('internal', 'Internal'), ('external', 'External')], required=True, default='internal', string='Smoking Type')
    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    weekly_list_delivery_type = fields.Selection([('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], 'Delivery type', required=True, default='daily')
    weekly_list_delivery_concept = fields.Many2one('hr_turei.cigarette_concept', required=True)


class HrServicesProvided(models.Model):
    _name = 'hr_turei.services_provided'

    name = fields.Char(string='Service')
    entity = fields.Char(string='Entity')


class HrTureiExternalStaff(models.Model):
    _name = 'hr_turei.external_staff'
    _order = 'name_related'
    _inherits = {'resource.resource': "resource_id"}

    @api.model
    def _default_image(self):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))

    # we need a related field in order to be able to sort the employee by name
    name_related = fields.Char(related='resource_id.name', string="Nombre", readonly=True, store=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], string='Gender', required=True)
    image = fields.Binary("Photo", default=_default_image, attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized photo", attachment=True,
        help="Medium-sized photo of the employee. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized photo", attachment=True,
        help="Small-sized photo of the employee. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    code = fields.Char('Code')
    carries_daily_smoking = fields.Boolean(string='Lleva asignación de fuma')
    packs_amount = fields.Selection([('1', '1'), ('2', '2')], string='Packs Amount', default='1')
    smoker = fields.Boolean(string='Smoker')
    brand_smoke_id = fields.Many2one('hr_sgp_integration.brand', string='Smoking brand')
    resource_id = fields.Many2one('resource.resource', string='Resource', ondelete='cascade', required=True, auto_join=True)
    active = fields.Boolean(string='Active', default=True)
    area_id = fields.Many2one('hr_turei.external_area', 'Area', required=True)
    service_ids = fields.Many2many('hr_turei.services_provided', 'hr_turei_external_staff_services_provided_rel', 'external_staff_id', 'service_provided_id', string='Services Provided', required=True)
    company_retired = fields.Boolean('Company Retired', required=True, default=False)
    permanent_disability = fields.Boolean('Permanent Disability', required=True, default=False)


class HrTureiExternalStaffAttendanceLine(models.Model):
    _name = 'hr_turei.external_staff_attendance.line'

    _sql_constraints = [
        ('attendance_external_staff_uniq', 'unique (attendance_id, external_staff_id)', 'There is already a line with the attendance for this person!'),
    ]

    days = fields.Integer('Days', required=True)
    external_staff_id = fields.Many2one('hr_turei.external_staff', 'Person', required=True)
    attendance_id = fields.Many2one('hr_turei.external_staff_attendance', 'Attendance', required=True)


class HrTureiExternalTemplateAttendance(models.Model):
    _name = 'hr_turei.external_staff_attendance'

    _sql_constraints = [
        ('area_period_uniq', 'unique (external_area_id, period_id)', 'There is already an attendance registry for this area in the selected period!'),
    ]

    @api.onchange('external_area_id', 'days')
    def _onchange_external_area_id(self):
        if self.external_area_id and self.days:
            ops = [(5, 0, 0)]
            for record in self.external_area_id.external_staff_ids:
                ops.append((0, 0, {'external_staff_id': record.id, 'days': self.days}))
            self.line_ids = ops

    @api.depends('period_id', 'external_area_id')
    def _compute_name(self):
        for record in self:
            if record.period_id:
                start_date = fields.Date.to_string(fields.Date.from_string(record.period_id.start_date))
                end_date = fields.Date.to_string(fields.Date.from_string(record.period_id.end_date))
                record.name = _('%s Attendance Registry from %s to %s') % (record.external_area_id.name, start_date, end_date)

    def _default_company_id(self):
        company_id = self.env['res.company']._company_default_get()
        return company_id

    company_id = fields.Many2one(comodel_name="res.company", string="Company", required=True,
                                 default=_default_company_id)
    name = fields.Char('Name', readonly=True, compute='_compute_name')
    period_id = fields.Many2one('hr_turei.smoke_period', 'Period', required=True)
    external_area_id = fields.Many2one('hr_turei.external_area', 'Area', required=True, domain="[('weekly_list_delivery_type', '=', 'daily')]")
    days = fields.Integer('Days', required=True, default=5)
    line_ids = fields.One2many('hr_turei.external_staff_attendance.line', 'attendance_id', 'Associated', required=True)



