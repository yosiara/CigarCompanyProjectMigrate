# -*- coding: utf-8 -*-

import logging

import psycopg2
import mysql.connector
import pymssql
import pymysql
from mysql.connector import errorcode

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger("info")


class DBExternalConnectorTemplate(models.Model):
    _name = "db_external_connector.template"
    _description = "Data Base Connector Template"
    _inherit = ["mail.thread"]

    # _connection = False

    name = fields.Char(string="Datasource Name", required=True)
    server = fields.Char(string="Server", required=True)
    port = fields.Char(string="Port", required=True)
    user = fields.Char(string="User", required=True)
    pwd = fields.Char(string="Password", required=True)
    dbname = fields.Char(string="Database Name", required=True)
    connector = fields.Selection(
        string=_("Connector"),
        selection=[
            ("psycopg2", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("pymysql", "PyMySQL"),
            ("pymssql", "MSSQL"),
        ],
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.user.company_id
    )
    application = fields.Selection(
        selection=[
            ("fastos", "Fastos"),
            ("versat", "Versat"),
            ("ocsinventory", "OCSInventory"),
        ],
        help="System to create conection. This field can be used in order to identify the connection...",
        string="Application",
    )

    # @api.one
    def action_test_connection(self):
        try:
            cnx = self.connect()
            cnx.close()
            self.message_post(body=_("Connection established successfully!!."))
        except Exception:
            self.message_post(
                body=_("Connection failed!!. Check your data connection.")
            )
            return False
        return True

    def connect(self):
        config = {
            "database": self.dbname,
            "host": self.server,
            "port": self.port,
            "user": self.user,
            "password": self.pwd,
        }

        if self.connector == "psycopg2":
            try:
                return psycopg2.connect(**config)
            except psycopg2.Error as err:
                print(err)

        elif self.connector == "mysql":
            try:
                return mysql.connector.connect(**config)
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    print("Database does not exist")
                else:
                    print(err)

        elif self.connector == "pymysql":
            try:
                return pymysql.connect(**config)
            except pymysql.Error as err:
                print(err)

        elif self.connector == "pymssql":
            try:
                return pymssql.connect(**config)
            except pymssql.Error as err:
                print(err)

        return None

    # def close(self):
    #     if self._connection:
    #         self._connection.close()
    #     return True
