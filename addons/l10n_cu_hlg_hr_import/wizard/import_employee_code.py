# -*- coding: utf-8 -*-
import logging
import traceback
from datetime import datetime, date

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger('INFO')


class ImportEmployeeCodeWizard(models.TransientModel):
    _name = "l10n_cu_hr_import.import_employee_code_wzd"

    def _get_default_connector(self):
        return self.env['db_external_connector.template'].search(
            [('application', '=', 'fastos')], limit=1
        ).id or False

    connector_id = fields.Many2one(
        'db_external_connector.template', 'Database', required=True, default=_get_default_connector
    )

    def action_import(self):
        obj = self
        if self._context.get('connector_id'):
            connection = self._context.get('connector_id').connect()
            obj = self.create({'connector_id': self._context.get('connector_id').id})
        else:
            connection = self.connector_id.connect()

        for employee in self.env['hr.employee'].search([]):
            code = self.get_empl_code(connection, tools.ustr(employee.identification_id))
            if code is not False:
                _logger.info(tools.ustr(code))                
                exist = self.env['hr.employee'].search([('code', '=', tools.ustr(code))])
                if len(exist) == 0 or (len(exist) == 1 and exist.id == employee.id):
                    employee.write({'code': tools.ustr(code), 'external_id': tools.ustr(code)})
        return True

    def get_empl_code(self, conn, ci=False):
        cursor = conn.cursor()
        try:
            if ci:
                query = """select CPT_Empleados.Id_Empleado from  CPT_Empleados Where CI='%s';""" % (tools.ustr(ci))
                cursor.execute(tools.ustr(query))
                result = cursor.fetchall()
                if len(result) and result[0][0] is not None:
                    return tools.ustr(result[0][0])
            cursor.close()
            return False
        except Exception, e:
            cursor.close()
            _logger.info(e)
            _logger.info(traceback.extract_stack())
            raise UserError(_("""The operation has not been completed. Please, check the connection of the Database
                                 and make sure to select the correct one..."""))

