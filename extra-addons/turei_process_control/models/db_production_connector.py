# -*- coding: utf-8 -*-

import psycopg2
import socket
from odoo import models, fields, api, tools
from odoo.exceptions import Warning

CONNECTORS = [('postgresql', 'PostgreSQL')]


class DBProductionConnector(models.Model):
    _name = "db_production_connector.template"

    _connection = False

    name = fields.Char(string='Datasource Name', required=True, default='DB Sistema de producción')
    server = fields.Char(string="Server", required=True, default='localhost')
    port = fields.Integer(string="Port", required=True, default=5432)
    user = fields.Char(string="User", required=True, default='odoov10')
    pwd = fields.Char(string="Password", required=True)
    dbname = fields.Char(string="Database Name", required=True)
    connector = fields.Selection(CONNECTORS, 'Connector', required=True, default='postgresql')

    @api.one
    def action_test_connection(self):
        if self.connector == 'postgresql':
            try:
                if self.checkServerListen():
                    conn = psycopg2.connect(
                        database=self.dbname, user=self.user, password=self.pwd, port=self.port, host=self.server)
                    conn.close()
                else:
                    raise Exception(u'imposible conectar con el servidor postgres.' + self.server)
            except Exception, e:
                raise Warning(u'Conexión Fallida:' + tools.ustr(e.message))
            raise Warning(u'Conexión ok')
        return True

    def connect(self):
        if self.connector == 'postgresql':
            try:
                if self.checkServerListen():
                    self._connection = psycopg2.connect(
                        database=self.dbname, user=self.user, password=self.pwd, port=self.port, host=self.server)
                    return self._connection
                return False
            except Exception, e:
                raise Warning(u'Conexión Fallida:' + tools.ustr(e.message))
        return False

    def close(self):
        if self._connection:
            self._connection.close()
        return True

    def checkServerListen(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        try:
            s.connect((self.server, self.port))
            s.close()
        except socket.error, ex:
            return False
        return True
