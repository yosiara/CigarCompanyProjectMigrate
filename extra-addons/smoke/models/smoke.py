# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging
_logger = logging.getLogger(__name__)

import re
from datetime import datetime, timedelta


class SmokeSmoke(models.Model):
    _name = "smoke.smoke"
    _description = "Smoke Model Main"
    _order = "date"

    concept_id = fields.Many2one(comodel_name="smoke.concept", string="Concept *", ondelete="restrict", required=True)

    date = fields.Date(string="Date *", required=True)

    amount = fields.Float(string="Quantity *", required=True)

    external_concept_id = fields.Integer(string="Concept ID *", required=True)

    order = fields.Char(string="Order", default="")

    # Get connection to the application
    def _get_connection(self, application):
        try:
            inst = self.env["db_external_connector.template"].search([("application", "=", application)], limit=1)
            if not inst:
                raise UserError(f"{application.title()} application data not found")
            cnx = inst.connect()
        except Exception as e:
            _logger.critical(f"We could not establish a connection. Error={e}")
            raise UserError(_(f"We could not establish a connection.\nPlease, check the connection of the {application.title()} Database..."))
        else:
            return cnx

    # Run queries
    def _execute_query(self, cursor, query):
        try:
            cursor.execute(query)
            records = cursor.fetchall()
        except Exception as e:
            _logger.critical(f"Execute Query Failed. Error={e}")
            raise UserError(_("Execute Query Failed. Please, check the connection of the Database and make sure to select the correct one..."))
        else:
            cursor.close()
            _logger.info("Data Obtained Successfully!!!")
            return records

    # Get date range
    def get_date_range(self):
        hoy = datetime.now()
        month_prev = hoy.month - 1 if hoy.month > 1 else 12
        year_month_prev = hoy.year if hoy.month > 1 else hoy.year - 1

        start_date = datetime(year_month_prev, month_prev, 1).date()
        end_date = (datetime(hoy.year, hoy.month, 1) - timedelta(days=1)).date()

        return start_date, end_date

    # Scheduled action to import smoke data
    @api.model
    def _cron_import_smoke_data(self):
        # Establish connection to the Versat database
        cnx = self._get_connection("versat")

        # Clean database in date range before importing
        start_date, end_date = self.get_date_range()
        self.search([("create_date", ">", end_date)]).unlink()
        self.concept_id.search([("create_date", ">", end_date)]).unlink()

        # Get names of previous concepts
        concept_recs = self.concept_id.search([])
        conceptArray = []
        if concept_recs:
            for it in concept_recs:
                conceptArray.append(it.name)

        # Get data from Versat database
        query = f"""
                SELECT fecha, sumacantidad, descripcion, idconcepto
                    FROM dbo.inv_documento
                        WHERE (idconcepto='64' or idconcepto='53') AND fecha BETWEEN '{start_date}' AND '{end_date}'
                """
        smokeData = sorted(
            self._execute_query(cursor=cnx.cursor(), query=query),
            key=lambda x: x[3],
            reverse=True,
        )

        # Close the connection and free up resources
        cnx.close()

        # Processing data...
        for i in smokeData:
            # Get order
            math = re.findall(r"(?:IPV|VALE|ORDEN).+$", i[2], flags=re.IGNORECASE)
            order_tmp = ""
            if math:
                order_tmp = "".join(math[0].split()).upper()
            
            # Get Concept
            concept = (" ".join(re.sub(r"(DEV[A-Z]*ON|IPV|VALE|ORDEN).*$","",i[2],flags=re.IGNORECASE,).split())).upper()

            if i[3] == 53 and order_tmp: # Get output concept
                inst = self.search(
                    [("order", "=", order_tmp), ("external_concept_id", "=", 64)],
                    limit=1,
                )
                if inst:
                    concept = inst.concept_id.name

            concept_inst = self.concept_id
            if concept not in conceptArray: # Create concept
                conceptArray.append(concept)
                data = {
                    "name": concept,
                }
                concept_inst = self.concept_id.create(data)
                _logger.info("Creating concept record...", data)

            # Create a record of warehouse outputs or returns
            concept_id_tmp = concept_inst.id if concept_inst else self.concept_id.search([("name", "=", concept)], limit=1).id
            data = {
                "date": i[0].date(),
                "concept_id": concept_id_tmp,
                "amount": round(i[1], 2),
                "order": order_tmp,
                "external_concept_id": i[3],
            }
            self.create(data)
            _logger.info("Creating smoking record...", data)
