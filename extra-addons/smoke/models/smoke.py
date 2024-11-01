# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging
import re
from datetime import datetime, timedelta
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SmokeSmoke(models.Model):
    _name = "smoke.smoke"

    _description = "Smoke Model Main"

    _order = "date"

    # def _get_default_connector(self):
    #     return (
    #         self.env["db_external_connector.template"]
    #         .search([("application", "=", "versat")], limit=1)
    #         .id
    #         or False
    #     )

    # connector_id = fields.Many2one(
    #     "db_external_connector.template",
    #     "Database",
    #     required=True,
    #     default=_get_default_connector,
    # )

    concept_id = fields.Many2one(
        string="Concept",
        comodel_name="smoke.concept",
        ondelete="restrict",
        required=True,
    )

    # external_id = fields.Integer(
    #     string="Integration with iddocumento in Versat db", required=True
    # )

    date = fields.Date(string="Date", required=True)

    amount = fields.Float(string="Amount", required=True)

    external_concept_id = fields.Integer(string="Concept ID", required=True)

    order = fields.Char(string="Order", default="")

    def _execute_query(self, cursor, query):
        try:
            cursor.execute(query)
            records = cursor.fetchall()
        except Exception:
            _logger.info(Exception)
            raise UserError(
                _(
                    """The operation has not been completed. Please, check the connection of the Database
                     and make sure to select the correct one..."""
                )
            )
        finally:
            cursor.close()
            print("Connection Closed Successfully!!")

        return records

    def get_date_range(self):
        hoy = datetime.now()
        month_prev = hoy.month - 1 if hoy.month > 1 else 12
        year_month_prev = hoy.year if hoy.month > 1 else hoy.year - 1

        start_date = f"{year_month_prev}-{month_prev:02d}-01"
        end_date = (
            datetime(year_month_prev, month_prev + 1, 1) - timedelta(days=1)
        ).date()

        return start_date, end_date

    @api.model
    def _cron_import_data_smoke(self):
        inst = self.env["db_external_connector.template"].search(
            [("application", "=", "versat")], limit=1
        )
        if not inst:
            raise UserError(
                _(
                    """The operation has not been completed. Please, check the connection of the Database..."""
                )
            )
        cnx = inst.connect()

        # Clear db in range date
        start_date, end_date = self.get_date_range()
        self.search([("create_date", ">", end_date)]).unlink()
        self.concept_id.search([("create_date", ">", end_date)]).unlink()

        concept_recs = self.concept_id.search([])
        conceptArray = []
        if concept_recs:
            for it in concept_recs:
                conceptArray.append(it.name)

        # Get Data Smoke
        query = f"""
                SELECT fecha, sumacantidad, descripcion, idconcepto
                    FROM dbo.inv_documento
                        WHERE (idconcepto='64' or idconcepto='53') AND fecha BETWEEN '{start_date}' AND '{end_date}'
                """
        dataSmoke = sorted(
            self._execute_query(cursor=cnx.cursor(), query=query),
            key=lambda x: x[3],
            reverse=True,
        )

        # Process and Insert Data
        for i in dataSmoke:
            math = re.findall(r"(?:IPV|VALE|ORDEN).+$", i[2], flags=re.IGNORECASE)
            order_tmp = ""
            if math:
                order_tmp = "".join(math[0].split()).upper()
            concept = (
                " ".join(
                    re.sub(
                        r"(DEV[A-Z]*ON|IPV|VALE|ORDEN).*$",
                        "",
                        i[2],
                        flags=re.IGNORECASE,
                    ).split()
                )
            ).upper()

            if i[3] == 53:
                inst = self.search(
                    [("order", "=", order_tmp), ("external_concept_id", "=", 64)],
                    limit=1,
                )
                print("****Inst: ", inst)
                if inst:
                    concept = inst.concept_id.name

            concept_inst = self.concept_id
            if concept not in conceptArray:
                conceptArray.append(concept)
                data = {
                    "name": concept,
                }
                concept_inst = self.concept_id.create(data)
                print("Data Concept", data)

            concept_id_tmp = (
                concept_inst.id
                if concept_inst
                else self.concept_id.search([("name", "=", concept)], limit=1).id
            )
            data = {
                "date": i[0].date(),
                "concept_id": concept_id_tmp,
                "amount": round(i[1], 2),
                "order": order_tmp,
                "external_concept_id": i[3],
            }
            self.create(data)

            print("Data All", data)
