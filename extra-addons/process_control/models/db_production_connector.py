# -*- coding: utf-8 -*-

import psycopg2
import socket
from odoo import models, fields, _
from odoo.exceptions import UserError, Warning

CONNECTORS = [('postgresql', 'PostgreSQL')]


class DBProductionConnector(models.Model):
    _name = 'process_control.db_production_connector'

    _connection = False

    name = fields.Char(string='Datasource *', required=True, default='DB Production System')
    server = fields.Char(string='Server *', required=True, default='localhost')
    port = fields.Integer(string='Port *', required=True, default=5432)
    user = fields.Char(string='User *', required=True, default='odoo18')
    pwd = fields.Char(string='Password *', required=True)
    dbname = fields.Char(string='Database *', required=True)
    connector = fields.Selection(CONNECTORS, 'Connector *', required=True, default='postgresql')

    def action_test_connection(self):
        if self.connector == 'postgresql':
            try:
                if self.checkServerListen():
                    conn = psycopg2.connect(
                        database=self.dbname,
                        user=self.user,
                        password=self.pwd,
                        port=self.port,
                        host=self.server
                    )
                    conn.close()
                else:
                    raise Exception(_('Unable to connect to the PostgreSQL server {}:{}').format(self.server, self.port))
            except Exception as e:
                raise UserError('Connection Failed: {}'.format(str(e)))
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Connection successful'),
                    'message': _('The connection to PostgreSQL was successful.'),
                    'type': 'success',
                    'sticky': False,
                }
            }
        return True

    def connect(self):
        if self.connector == 'postgresql':
            try:
                if self.checkServerListen():
                    self._connection = psycopg2.connect(
                        database=self.dbname,
                        user=self.user,
                        password=self.pwd,
                        port=self.port,
                        host=self.server
                    )
                    return self._connection
                else:
                    raise Exception('Unable to connect to the PostgreSQL server {}:{}'.format(self.server, self.port))
            except Exception as e:
                raise UserError('Connection failed when opening the connection: {}'.format(str(e)))
        return False

    def close(self):
        if self._connection:
            try:
                self._connection.close()
            except Exception as e:
                pass
            self._connection = False
        return True

    def checkServerListen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((self.server, self.port))
            s.close()
            return True
        except socket.error as ex:
            return False