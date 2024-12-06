# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import logging
from odoo.exceptions import ValidationError

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

try:
    import psycopg2
    import mysql.connector
    import pymssql
    import pymysql
except ImportError:
    raise ImportError(_("Python Library Import Error"))


class DBExternalConnectorTemplate(models.Model):
    _name = "db_external_connector.template"
    _description = "DataBase Connector Template"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Datasource *", required=True)
    server = fields.Char(string="Server *", required=True)
    port = fields.Integer(string="Port *", required=True)
    user = fields.Char(string="User *", required=True)
    pwd = fields.Char(string="Password *", required=True)
    dbname = fields.Char(string="Database *", required=True)
    connector = fields.Selection(
        selection=[
            ("psycopg2", "PostgreSQL"),
            ("mysql", "MySQL"),
            ("pymysql", "PyMySQL"),
            ("pymssql", "MSSQL"),
        ], string=("Connector *"), required=True, default="pymssql",
    )
    # company_id = fields.Many2one(
    #     "res.company", string="Company", default=lambda self: self.env.user.company_id
    # )
    application = fields.Selection(
        selection=[
            ("fastos", "Fastos"),
            ("versat", "Versat"),
            ("ocsinventory", "OCSInventory"),
        ], string="Application *", required=True, default="versat",
        help="System to connect to. This field will be used to identify the connection...",
    )

    @api.constrains("port")
    def _constrains_port(self):
        if self.port == 0:
            raise ValidationError(_("Please make sure to set a valid port"))

    @api.onchange("connector")
    def _onchange_connector(self):
        if self.connector == "psycopg2":
            self.port = 5432
        elif self.connector == "pymssql":
            self.port = 1433
        elif self.connector in ["mysql", "pymysql"]:
            self.port = 3306
            
    def connect(self):
        config = {
            "database": self.dbname,
            "host": self.server,
            "port": self.port,
            "user": self.user,
            "password": self.pwd,
        }
        try:
            match self.connector:
                case "psycopg2":
                    cnx = psycopg2.connect(**config)
                case "mysql":
                    cnx = mysql.connector.connect(**config)
                case "pymysql":
                    cnx = pymysql.connect(**config)
                case "pymssql":
                    cnx = pymssql.connect(**config)
                case other:
                    raise ValueError(f"Invalid Connector: {other}")
        except (psycopg2.Error, mysql.connector.Error, pymysql.Error, pymssql.Error, ValueError):
            _logger.exception("Database Connection Failed")
            raise
        else:
            _logger.info("Connection established successfully!!!.")
            return cnx

    def action_test_connection(self):
        try:
            cnx = self.connect()
        except Exception as e:
            _logger.critical(f"Test connection failed. Error={e}")
            self.message_post(body=_("Connection failed!!!. Check your data connection."))
            return False
        else:
            cnx.close()
            self.message_post(body=_("Connection established successfully!!!."))
            return True

