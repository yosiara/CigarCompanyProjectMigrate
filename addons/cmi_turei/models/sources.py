# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CmiLotesNoConforme(models.AbstractModel):
    _name = 'cmi_turei.source.lotes_no_conforme'
    _description = 'Lotes no conforme'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT SUM(coalesce(l.lotes_no_conforme,0)) as value, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_lotes_no_conforme l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                            GROUP BY p.anno, p.mes_numero;
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiDesempenoAtmosfera(models.AbstractModel):
    _name = 'cmi_turei.source.desempeno_atmosfera'
    _description = u'Programa para Minimizar las emisiones de gases y partículas polvo a la atmósfera'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, cumplido as value, total as plan
                            FROM schema_general.agg_desempeno_atmosfera
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiDesempenoResiduos(models.AbstractModel):
    _name = 'cmi_turei.source.desempeno_residuos'
    _description = u'Cumplimiento del programa para el manejo de residuos solidos y liquidos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, cumplido as value, total as plan
                            FROM schema_general.agg_desempeno_residuos_solidos
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiProgramaEducacionAmbiental(models.AbstractModel):
    _name = 'cmi_turei.source.educacion_ambiental'
    _description = u'Cumplimiento del programa de educación ambiental'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, cumplido as value, total as plan
                            FROM schema_general.agg_desempeno_educacion_ambiental
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiProgramaPortadoresEnergeticos(models.AbstractModel):
    _name = 'cmi_turei.source.portadores_energeticos'
    _description = u'Cumplimiento del programa para usar eficientemente los portadores energeticos, las materias primas, materiales e insumos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, cumplido as value, total as plan
                            FROM schema_general.agg_desempeno_portadores_energeticos
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiRequisitosLegales(models.AbstractModel):
    _name = 'cmi_turei.source.requisitos_legales'
    _description = u'Cumplimiento de los requisitos legales aplicables a la empresa'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, cumplen as value, (cumplen + incumplen) as plan
                            FROM schema_general.agg_requisitos_legales
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiVentasCigarrillos(models.AbstractModel):
    _name = 'cmi_turei.source.ventas_cigarrillos'
    _description = u'Ventas Cigarrillos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT 
                                    SUM(v.plan) as plan, SUM(v.real) as value, p.anno as year, p.mes_numero as month
                                    FROM schema_general.agg_plan_venta_cigarrillos v
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = v.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s )
                                    GROUP BY v.id_periodo, p.anno, p.mes_numero
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[2]), 'month': int(row[3]), 'value': row[1], 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    print e
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiVentasTabacoReconstituido(models.AbstractModel):
    _name = 'cmi_turei.source.ventas_tabaco_reconstituido'
    _description = u'Ventas Tabaco Reconstituido'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT 
                                    SUM(v.plan) as plan, SUM(v.real) as value, p.anno as year, p.mes_numero as month
                                    FROM schema_general.agg_plan_venta_tabaco_reconstituido v
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = v.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                                    GROUP BY v.id_periodo, p.anno, p.mes_numero
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[2]), 'month': int(row[3]), 'value': row[1], 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiIndiceCalidadManufactura(models.AbstractModel):
    _name = 'cmi_turei.source.indice_calidad_manufactura'
    _description = u'Indice de calidad en la manufactura'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT SUM(coalesce(l.real,0)) as real,SUM(coalesce(l.ponderacion,0)) as ponderacion, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_indice_calidad_manufactura l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                            GROUP BY p.anno, p.mes_numero;
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        value = (row[1]/row[0])/100.00 if row[0] else 0.00
                        res.append({'year': str(row[2]), 'month': int(row[3]), 'value': value})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanProduccionCigarrillos(models.AbstractModel):
    _name = 'cmi_turei.source.plan_produccion_cigarrillos'
    _description = u'Cumplimiento del plan de Producción de cigarrillos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            SUM(p.real) as value, SUM(p.plan) as plan, p.fecha_fin as date
                            FROM schema_general.agg_plan_produccion_rrhh p
                            WHERE p.fecha_fin >= Date(%s)
                            GROUP BY p.fecha_fin;
                    """, [str(params['date'])])
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': (row[0] if row[0] else 0.00)/100.00, 'plan': (row[1] if row[1] else 0.00)/100.00})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    print e
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanProduccionMensualCigarrillos(models.AbstractModel):
    _name = 'cmi_turei.source.plan_produccion_mensual_cigarrillos'
    _description = u'Cumplimiento del plan de Producción de cigarrillos mensual'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            SUM(p.real) as value, SUM(p.plan) as plan, p.fecha as date
                            FROM schema_general.agg_plan_produccion_rrhh_mensual p
                            WHERE p.fecha >= Date(%s)
                            GROUP BY p.fecha;
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': (row[0] if row[0] else 0.00)/100.00, 'plan': (row[1] if row[1] else 0.00)/100.00})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanProduccionTabacoReconstituido(models.AbstractModel):
    _name = 'cmi_turei.source.plan_tab_reconstituido'
    _description = u'Cumplimiento del plan de Producción de láminas de tabaco reconstituido'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            SUM(p.real) as value, SUM(p.plan) as plan, p.fecha_fin as date
                            FROM schema_general.agg_plan_tabaco_reconstituido_rrhh p
                            WHERE p.fecha_fin >= Date(%s)
                            GROUP BY p.fecha_fin
                            ORDER BY p.fecha_fin
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': (row[0] if row[0] else 0.00)/1000.00, 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    print e
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanProduccionTabacoReconstituidoMensual(models.AbstractModel):
    _name = 'cmi_turei.source.plan_tab_reconstituido_mensual'
    _description = u'Cumplimiento del plan de Producción de láminas de tabaco reconstituido mensual'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            SUM(p.real) as value, SUM(p.plan) as plan, p.fecha as date
                            FROM schema_general.agg_plan_tabaco_reconstituido_rrhh_mensual p
                            WHERE p.fecha >= Date(%s)
                            GROUP BY p.fecha
                            ORDER BY p.fecha
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': (row[0] if row[0] else 0.00)/1000.00, 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanMecanicoElectronico(models.AbstractModel):
    _name = 'cmi_turei.source.plan_mecanico_electronico'
    _description = u'Cumplimiento del plan de mantenimiento mecánico-electrónico'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    SUM(m.real) as value, SUM(m.plan) as plan, p.anno as year, p.mes_numero as month
                                    FROM schema_general.agg_plan_mecanico_electronico m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                     WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                                    GROUP BY m.id_periodo, p.anno, p.mes_numero
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[2]), 'month': int(row[3]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiDisponibilidadTecnicaIndustriaPrimario(models.AbstractModel):
    _name = 'cmi_turei.source.disp_tecnica_industria_primario'
    _description = u'Coeficiente disponibilidad técnica de la industria en el taller primario'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.cdt as value, p.anno as year, p.mes_numero as month
                                    FROM schema_general.agg_cdt_industria_mensual_primario m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiDisponibilidadTecnicaIndustriaSecundario(models.AbstractModel):
    _name = 'cmi_turei.source.disp_tecnica_industria'
    _description = u'Coeficiente disponibilidad técnica de la industria en el taller secundario'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.cdt as value, p.anno as year, p.mes_numero as month
                                    FROM schema_general.agg_cdt_industria_mensual m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiProgramaDignificacion(models.AbstractModel):
    _name = 'cmi_turei.source.indice_programa_dignificacion'
    _description = u'Índice de Cumplimiento de las acciones contempladas en el programa de dignificación'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real as value, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_programa_dignificacion m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPlanCapacitacion(models.AbstractModel):
    _name = 'cmi_turei.source.plan_capacitacion'
    _description = u'Cumplimiento del plan de capacitación'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_programa_capacitacion m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiDesempenoIndividual(models.AbstractModel):
    _name = 'cmi_turei.source.desempeno_individual'
    _description = u'Nivel de Desempeño Individual'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_desempeno_individual m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiClimaLaboral(models.AbstractModel):
    _name = 'cmi_turei.source.clima_laboral'
    _description = u'Índice de Calidad de Clima Laboral'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_clima_laboral m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiIndiceAusentismo(models.AbstractModel):
    _name = 'cmi_turei.source.indice_ausentismo'
    _description = u'Índice de ausentismo'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_indice_ausentismo m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiIndiceFluctuacionPersonal(models.AbstractModel):
    _name = 'cmi_turei.source.indice_fluctuacion_personal'
    _description = u'Índice de Fluctuación de Personal'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.real, p.anno as year, p.mes_numero as month, m.plan
                                    FROM schema_general.agg_indice_fluctuacion_personal m
                                    INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = m.id_periodo
                                    WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiAreasProtegidas(models.AbstractModel):
    _name = 'cmi_turei.source.areas_protegidas'
    _description = u'Total de áreas que se declaran Áreas Protegidas'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, protegidas as value, plan
                            FROM schema_general.agg_areas_protegidas
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiControlRiesgos(models.AbstractModel):
    _name = 'cmi_turei.source.control_riesgos'
    _description = 'Cumplimiento del Programa Gestión de Riesgos Laborales'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.real as value, l.plan, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_control_riesgos l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[2]), 'month': int(row[3]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiChequeosMedicos(models.AbstractModel):
    _name = 'cmi_turei.source.chequeos_medicos'
    _description = 'Cumplimiento del programa anual de chequeos médicos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.plan, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_chequeos_medicos l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPrespProteccionPersonalCUC(models.AbstractModel):
    _name = 'cmi_turei.source.presp_cuc_proteccion_personal'
    _description = 'Cantidad de presupuesto(CUC) en adquisición de medios de protección personal'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.cuc as plan, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_presupuesto_proteccion_personal l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s AND p.mes_numero >= %s ) 
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPrespProteccionPersonalCUP(models.AbstractModel):
    _name = 'cmi_turei.source.presp_cup_proteccion_personal'
    _description = 'Cantidad de presupuesto(CUP) en adquisición de medios de protección personal'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.cup as plan, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_presupuesto_proteccion_personal l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s  AND p.mes_numero >= %s  )
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiPrespProteccionPersonalTOTAL(models.AbstractModel):
    _name = 'cmi_turei.source.presp_total_proteccion_personal'
    _description = 'Cantidad de presupuesto(TOTAL) en adquisición de medios de protección personal'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.ambas as plan, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_presupuesto_proteccion_personal l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s  AND p.mes_numero >= %s  )
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'plan': row[0]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiMedidasAutocontrol(models.AbstractModel):
    _name = 'cmi_turei.source.medidas_autocontrol'
    _description = u'Cumplimiento de planes de medidas del autocontrol'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, real as value, plan
                            FROM schema_general.agg_medidas_autocontrol
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiControlInterno(models.AbstractModel):
    _name = 'cmi_turei.source.control_interno'
    _description = u'Cumplimiento de las acciones de control interno'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, real as value, plan
                            FROM schema_general.agg_control_interno
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiControlExterno(models.AbstractModel):
    _name = 'cmi_turei.source.control_externo'
    _description = u'Cumplimiento de planes de medidas de los controles externos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, real as value, plan
                            FROM schema_general.agg_control_externo
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiEficaciaPrevencionRiesgos(models.AbstractModel):
    _name = 'cmi_turei.source.eficacia_prevencion_riesgos'
    _description = u'Eficacia del Plan de prevención de riesgos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT l.eficacia as value, p.anno as year, p.mes_numero as month
                            FROM schema_general.agg_eficacia_prevencion_riesgos l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s  AND p.mes_numero >= %s  )
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiCumplValoresInversiones(models.AbstractModel):
    _name = 'cmi_turei.source.cumplimiento_inversiones'
    _description = u'Cumplimiento en valores de la inversión'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT ABS(l.saldo) as value, p.anno as year, p.mes_numero as month
                            FROM schema_economia.agg_cumplimiento_inversiones l
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = l.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s  AND p.mes_numero >= %s  )
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiRelGastosIngresos(models.AbstractModel):
    _name = 'cmi_turei.source.rel_gastos_ingresos'
    _description = u'Relación Gastos Totales/Peso de Ingreso Total'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['month']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT r.coeficiente as value, p.anno as year, p.mes_numero as month
                            FROM schema_economia.agg_rel_gastos_ingresos r
                            INNER JOIN schema_economia.dim_periodo p ON p.id_periodo = r.id_periodo
                            WHERE ( p.anno > %s ) OR ( p.anno = %s  AND p.mes_numero >= %s  )
                    """, (params['year'], params['year'], params['month']))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[1]), 'month': int(row[2]), 'value': row[0]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoTabacoNegro(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_tabaco_negro'
    _description = u'Consumo de tabaco negro'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            c.norma_real as value, c.norma_plan as plan, c.fecha_fin as date
                            FROM schema_general.agg_consumo_tabaco c
							INNER JOIN schema_general.dim_tipo_tabaco tp ON tp.id = c.id_tipo_tabaco
                            WHERE c.fecha_fin >= Date(%s) and tp.id_sgp = 2
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoTabacoRubio(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_tabaco_rubio'
    _description = u'Consumo de tabaco rubio'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            c.norma_real as value, c.norma_plan as plan, c.fecha_fin as date
                            FROM schema_general.agg_consumo_tabaco c
							INNER JOIN schema_general.dim_tipo_tabaco tp ON tp.id = c.id_tipo_tabaco
                            WHERE c.fecha_fin >= Date(%s) and tp.id_sgp = 1
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoCajasCarton(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_cajas_carton'
    _description = u'Consumo de Cajas de cartón corrugado'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                            FROM schema_general.agg_consumo_materiales m
							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                            WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 10
                    """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoSellos(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_sellos'
    _description = u'Consumo de sellos'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 5
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPegamentoLineaUnoCajetillas(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_peg_linea_caj'
    _description = u'Consumo de Pegamento L 1 (Cajetillas)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 19
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPegamentoLineaUnoCigarrillos(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_peg_linea_cig'
    _description = u'Consumo de Pegamento L 1 (Cigarrillos)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 20
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPolipropileno(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_polipropileno'
    _description = u'Consumo de Polipropileno'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 8
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoEnvolturaB1(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_envoltura_b1'
    _description = u'Consumo de Envoltura (negro) B1'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 17
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoMarquillaB1(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_marquilla_b1'
    _description = u'Consumo de Marquilla (negro) B1'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 16
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoMarquillaNegros(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_marq_negros'
    _description = u'Consumo de Marquillas (negros)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 3
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoEnvolturaRubios(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_envoltura_rubios'
    _description = u'Consumo de Envolturas (rubios)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 7
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoEnvolturaNegros(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_envoltura_negros'
    _description = u'Consumo de Envolturas (negros)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 6
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoMarquillasRubios(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_marquillas_rubios'
    _description = u'Consumo de Marquillas (rubios)'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 4
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPapelVelin(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_papel_velin'
    _description = u'Consumo de Papel cigarro velin'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 1
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoCintaRasgar(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_cinta_rasgar'
    _description = u'Consumo de Cinta para rasgar'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 9
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPapelBerge(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_papel_berge'
    _description = u'Consumo de Papel cigarro Berge'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 2
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoPegamentoHoltMelt(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_peg_holt_melt'
    _description = u'Consumo de Pegamento Holt Melt'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 12
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiConsumoAcetatoPegamento(models.AbstractModel):
    _name = 'cmi_turei.source.consumo_acetato'
    _description = u'Consumo de Pegamento Acetato'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['date']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                                    SELECT
                                    m.norma_real as value, m.norma_plan as plan, m.fecha_fin as date
                                    FROM schema_general.agg_consumo_materiales m
        							INNER JOIN schema_general.dim_materia_prima_pis mt ON mt.id = m.id_materia_prima_pis
                                    WHERE m.fecha_fin >= Date(%s) and mt.id_sgp = 11
                            """, (str(params['date']),))
                    res = []
                    for row in cursor:
                        res.append({'date': str(row[2]), 'value': row[0], 'plan': row[1]})
                    cursor.close()
                    connection.close()
                except Exception:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                                 the Database and make sure to select the correct one..."""))
                return res


class CmiMantenimientoTransporte(models.AbstractModel):
    _name = 'cmi_turei.source.mantenimiento_transporte'
    _description = u'Cumplimiento del plan de mantenimiento transporte'

    cmi_source = fields.Boolean('CMI Source', required=True)

    @api.multi
    def get_values(self, params={}):
        if params['year'] and params['trimester']:
            if self.env.user.company_id and self.env.user.company_id.dw_conn_id:
                try:
                    connection = self.env.user.company_id.dw_conn_id.connect()
                    cursor = connection.cursor()
                    cursor.execute("""
                            SELECT
                            anno as year, trimestre as trimester, real_total as value, plan_total as plan
                            FROM schema_general.agg_mantenimiento_transporte
                            WHERE ( anno > %s ) or ( anno = %s and trimestre >= %s )
                    """, (str(params['year']), str(params['year']), str(params['trimester'])))
                    res = []
                    for row in cursor:
                        res.append({'year': str(row[0]), 'trimester': str(row[1]), 'value': row[2], 'plan': row[3]})
                    cursor.close()
                    connection.close()
                except Exception, e:
                    raise UserError(_("""The operation has not been completed. Please, check the connection of 
                                         the Database and make sure to select the correct one..."""))
                return res