# -*- coding: utf-8 -*-


from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class Busqueda(models.TransientModel):
    _name = 'app_seleccion.wzd_breferenciap'

    partner_name_id = fields.Many2one('hr.applicant', string='Candidato',track_visibility='onchange',domain=[('estado','=','proceso')])

    #validar que se introduzca el nombre del candidato
    @api.constrains('partner_name_id')
    def _check_job(self):
        if not self.partner_name_id :
            raise ValidationError(_("Debe introducir el nombre del candidato!!"))

    @api.multi
    def imprimir(self):
        candidato_id = self.env['hr.applicant'].search([('id', '=', self.partner_name_id.id)])
        municipio = candidato_id.municipality_name
        jobs = candidato_id.nombre_trabajo
        fecha_hoy = fields.Date.today()

        datas = {
            'name': candidato_id.partner_name,
            'job_id':  jobs,
            'ci': candidato_id.ci,
            'ubicacion_laboral': candidato_id.ubicacion_laboral_actual,
            'direccion_laboral': candidato_id.direccion_laboral_actual,
            'direccion_particular': candidato_id.direccion_particular,
            'fecha': fecha_hoy,
            'municipio': municipio,

        }
        print datas


        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'app_seleccion.print_breferenciap_report',
                    'datas': datas,
                }


