# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Evaluar(models.TransientModel):
    _name = 'app_seleccion.wzd_evaluar'

    estudiante_id = fields.Many2one('hr.applicant', string='Estudiante',track_visibility='onchange')

    evaluacion_id = fields.One2many(comodel_name='app_seleccion.evaluacion',inverse_name='estudiante_id',string='Evaluación')


	

    #validar que se introduzca el nombre del candidato
    @api.constrains('partner_name_id')
    def _check_job(self):
        if not self.partner_name_id :
            raise ValidationError(_("Debe introducir el nombre del estudiante!!"))

    @api.multi
    def imprimir(self):
        candidato_id = self.env['hr.applicant'].search([('id', '=', self.partner_name_id.id)])
        jobs = candidato_id.nombre_trabajo
        fecha_hoy = fields.Date.today()

        datas = {
            'name': candidato_id.partner_name,
            'job_id':  jobs,
            'fecha': fecha_hoy,

        }
        print datas


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_rvsociolaboral_report',
                    'datas': datas,
                }


