# -*- coding: utf-8 -*-


from odoo import models, fields, tools


class HrTureiTeOvercomplianceWzd(models.TransientModel):
    _name = 'hr_turei.te_overcompliance_wzd'

    def _get_default_connection(self):
        return self.env['db_external_connector.template'].search([('application', '=', 'sgp')], limit=1)

    connection_id = fields.Many2one('db_external_connector.template', 'Connection SGP', required=True, default=_get_default_connection)
    start_date = fields.Date('Start Date', required=True, default=fields.Date.context_today)
    end_date = fields.Date('End Date', required=True, default=fields.Date.context_today)
    turn_id = fields.Many2one('hr_sgp_integration.turn', 'Turn')
    module_id = fields.Many2one('hr_sgp_integration.module', 'Module')
    plan = fields.Float('Plan', readonly=True)
    real = fields.Float('Real', readonly=True)
    percent = fields.Float('Percent', readonly=True)

    def calculate(self):

        connection = self.connection_id.connect()
        cursor = connection.cursor()

        params = [self.start_date, self.end_date]
        query_plan = u"""SELECT
                    Sum("public".pt_plan_te_distribucion.plan)
                    FROM
                    "public".pt_plan_te_distribucion
                    WHERE
                    "public".pt_plan_te_distribucion.fecha >= '%s' and 
                    "public".pt_plan_te_distribucion.fecha <= '%s'"""

        query_production = u"""SELECT
                    CASE WHEN (Sum("public".pt_produccion_terminada.cantidad_producida)) IS NULL THEN
                    (0) ELSE (Sum("public".pt_produccion_terminada.cantidad_producida)) END AS prod
                    FROM
                    "public".pt_produccion_terminada
                    WHERE
                    "public".pt_produccion_terminada.fecha >= '%s' and 
                    "public".pt_produccion_terminada.fecha <= '%s'
                    """

        if self.turn_id:
            params.append(self.turn_id)
            query_plan += u' AND "public".pt_plan_te_distribucion.id_turno = %s'
            query_production += u' AND "public".pt_produccion_terminada.id_turno = %s'

        if self.module_id:
            params.append(self.module_id)
            query_plan += u' AND "public".pt_plan_te_distribucion.id_modulo = %s'
            query_production += u' AND "public".pt_produccion_terminada.id_modulo = %s'

        cursor.execute(query_plan % tuple(params))
        plan = cursor.fetchall()

        cursor.execute(query_production % tuple(params))
        production = cursor.fetchall()
        porciento_cumplimiento = production[0][0] * 100.00
        if plan[0][0] is not None and plan[0][0] > 0:
            porciento_cumplimiento = (production[0][0] * 100.00) / plan[0][0]

        cursor.close()
        connection.close()
        self.plan = plan[0][0] if plan[0][0] is not None else 0.0
        self.real = production[0][0] if production[0][0] is not None else 0.0
        self.percent = porciento_cumplimiento
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr_turei.te_overcompliance_wzd',
            'type': 'ir.actions.do_nothing',
            'target': 'new'
        }


