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
        string="Concepts",
        comodel_name="smoke.concepts",
        ondelete="restrict",
    )

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

    def _get_date_range(self):
        hoy = datetime.now()
        month_prev = hoy.month - 1 if hoy.month > 1 else 12
        year_month_prev = hoy.year if hoy.month > 1 else hoy.year - 1

        start_date = f"{year_month_prev}-{month_prev:02d}-01"
        end_date = (
            datetime(year_month_prev, month_prev + 1, 1) - timedelta(days=1)
        ).date()

        return start_date, end_date

    def _cron_import_data_smoke(self):
        inst = self.env["db_external_connector.template"].search(
            [("application", "=", "versat")], limit=1
        )
        cnx = inst.connect()
        if not cnx:
            raise UserError(
                _(
                    """The operation has not been completed. Please, check the connection of the Database..."""
                )
            )

        # Get Date Range
        start_date, end_date = self._get_date_range()

        # Get Data Smoke
        query = f"""
                SELECT iddocumento, fecha, sumacantidad, descripcion, idconcepto
                    FROM dbo.inv_documento
                        WHERE (idconcepto='64' or idconcepto='53') AND fecha BETWEEN '{start_date}' AND '{end_date}'
                """
        dataSmoke = sorted(
            self._execute_query(cursor=cnx.cursor(), query=query),
            key=lambda x: x[4],
            reverse=True,
        )

        # Process and Insert Data
        conceptArray = []
        for i in dataSmoke:
            # patron = r"(?:IPV|VALE|ORDEN.*$"
            order = re.findall(r"(IPV|VALE|ORDEN).*$", i[3])
            # order = match[-1] if match else ""
            concept = (
                " ".join(
                    re.sub(
                        r"(DEV[A-Z]*ON|IPV|VALE|ORDEN).*$",
                        "",
                        i[3],
                        flags=re.IGNORECASE,
                    ).split()
                )
            ).upper()

            # if i[4] == 53:
            #     inst = self.search([('order', '=', order), ('external_concept_id', '=', 64)], limit=1)
            #         if inst:
            #             concept = inst.concept
            if concept not in conceptArray:
                conceptArray.append(concept)
                # self.concept_id = self.env("smoke.concepts").create({"date": i[1].date(), "concept": concept, "external_concept_id": i[4]})

            print("Data Select", i)
            print(
                "Data a Insertar",
                i[0],
                " Type: ",
                type(i[0]),
                i[1].date(),
                round(i[2], 2),
                concept,
                " Order: ",
                order,
            )
            # self.create(
            #     {
            #         "external_id": i[0],
            #         "date": i[1],
            #         "amount": i[2],
            #         "order": order,
            #         "external_concept_id": i[4],
            #     }
            # )
