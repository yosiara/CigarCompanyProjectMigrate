# -*- coding: utf-8 -*-

import logging
from sys import platform

import psycopg2
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

_logger = logging.getLogger('info')
CONNECTORS = [('postgresql', 'PostgreSQL')]

try:
    if platform == 'linux2':
        import pymssql as connector
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
    elif platform == 'win32':
        import pypyodbc as connector
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
except (ImportError, AssertionError):
    _logger.info('MsSQL not available. Please install "mssql" python package.')

try:
    if platform == 'win32':
        import pymysql as MySQLdb
    else:
        import MySQLdb

    CONNECTORS.append(('mysql', 'MySQL'))
except (ImportError, AssertionError):
    _logger.info('MySQL not available. Please install "mysqldb" python package.')


class DBExternalConnector(models.Model):
    _name = "db_external_connector.template"
    _description = "db_external_connector.template"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _connection = False

    name = fields.Char(string='Datasource Name', required=True)
    server = fields.Char(string="Server", required=True)
    port = fields.Char(string="Port", required=True)
    user = fields.Char(string="User", required=True)
    pwd = fields.Char(string="Password", required=True)
    dbname = fields.Char(string="Database Name", required=True)
    connector = fields.Selection(CONNECTORS, 'Connector', required=True, default='postgresql')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    application = fields.Selection(
        selection=[('fastos', 'Fastos'), ('versat', 'Versat'), ('rodas', 'Rodas'), ('assets', 'Assets')],
        help='System to create conection. This field can be used in order to identify the connection...',
        string='Application',
    )

    @api.one
    def action_test_connection(self):
        data = {
            'Driver': '{SQL Server}',
            'database': self.dbname,
            'Server': self.server,
            'port': self.port,
            'uid': self.user,
            'pwd': self.pwd,
        }

        if self.connector == 'postgresql':
            try:
                conn = psycopg2.connect(
                    database=data['database'], user=data['uid'], password=data['pwd'],
                    port=data['port'], host=data['Server']
                )
                conn.close()
                self.message_post(body=_('Connection established successfully!!.'))

            except Exception:
                self.message_post(body=_('Connection failed!!. Check your data connection.'))

        if self.connector == 'mysql':
            try:
                conn = MySQLdb.connect(
                    host=data['Server'], user=data['uid'], passwd=data['pwd'],
                    db=data['database'], port=int(data['port'])
                )
                conn.close()
                self.message_post(body=_('Connection established successfully!!.'))

            except Exception:
                self.message_post(body=_('Connection failed!!. Check your data connection.'))

        elif platform == 'linux2' and self.connector == 'mssql':
            try:
                conn = connector.connect(
                    host=data['Server'], port=data['port'], user=data['uid'], password=data['pwd'],
                    database=data['database'],
                )

                conn.close()
                self.message_post(body=_('Connection established successfully!!.'))

            except Exception:
                self.message_post(body=_('Connection failed!!. Check your data connection.'))
        else:
            try:
                conn = connector.connect(**data)
                self.message_post(body=_('Connection established successfully!!.'))
                conn.close()

            except Exception:
                self.message_post(body=_('Connection failed!!. Check your data connection.'))

        return True

    def connect(self):
        data = {
            'Driver': '{SQL Server}',
            'database': self.dbname,
            'Server': self.server,
            'port': self.port,
            'uid': self.user,
            'pwd': self.pwd,
        }

        if self.connector == 'postgresql':
            try:
                self._connection = psycopg2.connect(
                    database=data['database'], user=data['uid'], password=data['pwd'],
                    port=data['port'], host=data['Server']
                )

                return self._connection

            except Exception:
                raise UserError(_('Connection failed!!. Check your data connection.'))

        if self.connector == 'mysql':
            try:
                self._connection = MySQLdb.connect(
                    host=data['Server'], user=data['uid'], passwd=data['pwd'],
                    db=data['database'], port=int(data['port'])
                )
                return self._connection

            except Exception:
                raise UserError('Connection failed!!. Check your data connection.')

        if self.connector == 'mysql':
            try:
                self._connection = MySQLdb.connect(
                    host=data['Server'], user=data['uid'], passwd=data['pwd'],
                    db=data['database'], port=int(data['port'])
                )
                return self._connection

            except Exception:
                raise UserError('Connection failed!!. Check your data connection.')

        elif platform == 'linux2' and self.connector == 'mssql':
            try:
                self._connection = connector.connect(
                    host=data['Server'], port=data['port'], user=data['uid'], password=data['pwd'],
                    database=data['database'], autocommit=True,
                )

                return self._connection

            except Exception:
                raise UserError(_('Connection failed!!. Check your data connection.'))

        elif platform == 'win32' and self.connector == 'mssql':
            try:
                self._connection = connector.connect(autocommit=True, **data)
                return self._connection

            except Exception:
                raise UserError(_('Connection failed!!. Check your data connection.'))

        return None

    def close(self):
        if self._connection:
            self._connection.close()
        return True
