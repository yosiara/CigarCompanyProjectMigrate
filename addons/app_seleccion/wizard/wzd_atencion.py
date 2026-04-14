# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Atencion(models.TransientModel):
    _name = 'app_seleccion.wzd_atencion'

    partner_name_id = fields.Many2one('hr.applicant',string='Candidato',track_visibility='onchange',domain=[('estado','=','proceso')])


    #validar que se introduzca el nombre del candidato
    @api.constrains('partner_name_id')
    def _check_job(self):
        if not self.partner_name_id :
            raise ValidationError(_("Debe introducir el nombre del candidato!!"))


    @api.multi
    def imprimir(self):
        candidato_id = self.env['hr.applicant'].search([('id', '=', self.partner_name_id.id)])
        user_id = self.env.user.id

        empleado = self.env['hr.employee'].search([('user_id', '=', user_id)])
        job_empleado = empleado.job_id.name

        jobs = candidato_id.nombre_trabajo
        fecha_hoy = fields.Date.today()

        datas = {
            'name': candidato_id.partner_name,
            'job_id':  jobs,
            'job_empleado': job_empleado,
            'fecha': fecha_hoy,
        }
        print datas


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_atencion_report',
                    'datas': datas,
                }


