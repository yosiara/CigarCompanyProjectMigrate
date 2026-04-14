# -*- coding: utf-8 -*-

import logging

from odoo.fields import Many2one, Selection
from odoo.models import TransientModel
from odoo.tools import ustr


class ImportWizard(TransientModel):
    _name = 'fastos.import_wizard'
    _description = 'fastos.import_wizard'

    connector_id = Many2one('db_external_connector.template', string='Database', required=True)
    action = Selection([('employees', 'Import employees...')], default='employees', string='Import')

    def action_import(self):
        if self.action in ['employees']:
            return self.action_import_empployees()

    def action_import_empployees(self):
        connection = self.connector_id.connect()
        cursor = connection.cursor()

        query = """SELECT DISTINCT c.NombreCargo, c.Id_Cargo
                   FROM CPT_Empleados e
                   INNER JOIN CPT_Cargos c on e.Id_Cargo = c.Id_Cargo
                   INNER JOIN CPT_Departamentos d on e.Id_Departamento = d.Id_Departamento
                   INNER JOIN CPT_Areas a ON a.Id_Area=d.Id_Area
                   Where e.Id_Area=d.Id_Area AND e.Id_Departamento = d.Id_Departamento
                   Order BY c.NombreCargo, c.Id_Cargo"""

        cursor.execute(query)
        job_obj = self.env['hr.job']

        for row in cursor:
            values = {
                'name': ustr(row[0]),
                'external_id': ustr(row[1])
            }

            ids_job = job_obj.search([('external_id', '=', ustr(row[1]))])

            if len(ids_job) == 0:
                job_obj.create(values)
            else:
                values.pop('external_id')
                ids_job.write(values)

        return True

ImportWizard()
