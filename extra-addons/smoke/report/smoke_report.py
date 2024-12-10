# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

import re

class ReportSmoke(models.AbstractModel):
    _name = "report.smoke.report_smoke"
    _description = "Smoke Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        # Variable declarations
        objConcept = self.env["smoke.concept"]
        dataConcept = self.env["smoke.concept"]
        objSmoke = self.env["smoke.smoke"]
        dataSmoke = self.env["smoke.smoke"]
        cantSal = []
        cantDev = []
        totalSal = 0.00
        totalDev = 0.00
        totalSalCS = 0.00
        totalDevCS = 0.00
        desgloseCS = []
        concepts = []
        farol = 0.00
        cajetillas = 0.00
        flagCS = False

        # Obtain and prepare data
        if data["concept_id"]:
            domain = [
                ("date", ">=", data["start_date"]),
                ("date", "<=", data["end_date"]),
                ("concept_id", "=", data["concept_id"]),
            ]
            dataSmoke = objSmoke.search(domain)
            dataConcept = objConcept.browse(data["concept_id"])
        else:
            domain = [
                ("date", ">=", data["start_date"]),
                ("date", "<=", data["end_date"]),
            ]
            dataSmoke = objSmoke.search(domain)
            ids = []
            for i in dataSmoke:
                if i.concept_id.id not in ids:
                    ids.append(i.concept_id.id)
            dataConcept = objConcept.browse(ids)
            flagCS = True

        # Processing data...
        for i in dataConcept:
            sumcantSal = 0.00
            sumcantDev = 0.00
            flag = False
            for it in dataSmoke:
                if i.id == it.concept_id.id:
                    if "FAROL" in i.name:
                        farol += it.amount
                    else:
                        cajetillas += it.amount
                    if re.search(r"^(CS).*$", i.name):
                        desgloseCS.append(it)
                        if it.external_concept_id == 64:
                            totalSalCS += it.amount
                        else:
                            totalDevCS += it.amount
                        flag = True
                        continue
                    if it.external_concept_id == 64:
                        sumcantSal += it.amount
                        totalSal += it.amount
                    else:
                        sumcantDev += it.amount
                        totalDev += it.amount
            if not flag:
                concepts.append(i.name)
                cantSal.append(sumcantSal)
                cantDev.append(sumcantDev)

        return {
            "farol": farol,
            "cajetillas": cajetillas,
            "totalSal": totalSal,
            "totalDev": totalDev,
            "totalSalCS": totalSalCS,
            "totalDevCS": totalDevCS,
            "concepts": concepts,
            "cantSal": cantSal,
            "cantDev": cantDev,
            "desgloseCS": desgloseCS,
            "flagCS": flagCS,
        }
