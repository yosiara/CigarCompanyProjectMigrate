# -*- coding: utf-8 -*-

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError

import re

_logger = logging.getLogger(__name__)


class ReportSmoke(models.TransientModel):
    _name = "report.smoke.report_smoke"
    _description = "Smoke Report"

    def _get_default_connector(self):
        return (
            self.env["db_external_connector.template"]
            .search([("application", "=", "versat")], limit=1)
            .id
            or False
        )

    connector_id = fields.Many2one(
        "db_external_connector.template",
        "Database",
        required=True,
        default=_get_default_connector,
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

    def _getData(self, data, sal_dev, flag=False):
        it = 0
        total = 0.0
        for i in sal_dev:
            total += float(i[2])
            if flag:
                if "farol" in i[1].lower():
                    data["farol"] += float(i[2])
                else:
                    data["cajetillas"] += float(i[2])
                patron = r"(IPV|VALE|ORDEN).*$"
            else:
                patron = r"(DEV[A-Z]*ON|IPV|VALE|ORDEN).*$"

            concept = " ".join(re.sub(patron, "", i[1], flags=re.IGNORECASE).split())

            if re.search(r"^(cs)\s+.*$", concept.lower()):
                if flag:
                    data["CSDesglose"].append(i)
                concept = "CARTA DE SOLICITUD"

            if concept not in data["conceptArray"]:
                data["conceptArray"].insert(it, concept)
                j = i
                sumaCant = 0.0
                for j in sal_dev:
                    concept2 = " ".join(
                        re.sub(patron, "", j[1], flags=re.IGNORECASE).split()
                    )
                    if re.search(r"^(cs)\s+.*$", concept2.lower()):
                        sumaCant += float(j[2])
                        continue
                    if concept == concept2:
                        sumaCant += float(j[2])
                data["cantArray"].insert(it, sumaCant)
                it += 1
        data["cantArray"].append(total)

        return data

    @api.model
    def _get_report_values(self, docids, data=None):
        obj = self

        if not self.connector_id:
            try:
                obj = self.create({"connector_id": self._get_default_connector()})
            except Exception:
                _logger.info(Exception)
                raise UserError(
                    _("""Debe crear la conexion a la base de datos en configuracion""")
                )
        cnx = obj.connector_id.connect()

        # Salidas del almacen
        query = f"""
                SELECT fecha, descripcion, sumacantidad
                FROM dbo.inv_documento
                WHERE idconcepto = '64' AND fecha BETWEEN '{data["start_date"]}' AND '{data["end_date"]}'
                GROUP BY fecha, descripcion, sumacantidad
            """
        salidas = self._execute_query(cursor=cnx.cursor(), query=query)
        for i in salidas:
            print("SalidasConcept----------> ", i[1])

        datas = {
            "farol": 0.0,
            "cajetillas": 0.0,
            "conceptArray": [],
            "cantArray": [],
            "CSDesglose": [],
        }
        dataSalidas = self._getData(data=datas, sal_dev=salidas, flag=True)
        print("dataSalidas----------> ", dataSalidas)

        # Devoluciones al almacen
        query = f"""
                SELECT fecha, descripcion, sumacantidad
                FROM dbo.inv_documento
                WHERE idconcepto = '53' AND fecha BETWEEN '{data["start_date"]}' AND '{data["end_date"]}'
                GROUP BY fecha, descripcion, sumacantidad
            """
        devoluciones = self._execute_query(cursor=cnx.cursor(), query=query)
        for i in devoluciones:
            print("devolucionesConcept----------> ", i[1])

        datas = {
            "conceptArray": [],
            "cantArray": [0] * (len(dataSalidas["cantArray"]) - 1),
        }
        dataDevoluciones = self._getData(data=datas, sal_dev=devoluciones)
        print("dataDevoluciones------->", dataDevoluciones)

        for i in range(len(dataDevoluciones["conceptArray"])):
            try:
                index = dataSalidas["conceptArray"].index(
                    dataDevoluciones["conceptArray"][i]
                )
                element = dataDevoluciones["cantArray"].pop(i)
                dataDevoluciones["cantArray"][index] = element
            except ValueError:
                raise UserError(
                    _(
                        "Invalid concept in warehouse returns: "
                        + dataDevoluciones["conceptArray"][i]
                        + " no es existe en salidas"
                    )
                )
        dataSalidas["conceptArray"].append("TOTAL")

        return {
            "farol": dataSalidas["farol"],
            "cajetillas": dataSalidas["cajetillas"],
            "concepArray": dataSalidas["conceptArray"],
            "cantSalidas": dataSalidas["cantArray"],
            "cantDevoluciones": dataDevoluciones["cantArray"],
            "CSDesglose": dataSalidas["CSDesglose"],
        }
