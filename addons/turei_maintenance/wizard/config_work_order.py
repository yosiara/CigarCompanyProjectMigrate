# -*- coding: utf-8 -*-

import logging
from odoo.fields import Selection, Binary, Char
from odoo.models import TransientModel
from odoo.exceptions import UserError

_logger = logging.getLogger('INFO')


class ConfigWorkOrder(TransientModel):
    _name = 'turei_maintenance.config_work_order'
    _description = 'turei_maintenance.config_work_order'

    action = Selection([('upload_work_order', 'Cargar Orden de Trabajo'),
                        ('versat_work_order', 'Cargar Orden de Trabajo del VERSAT'),
                        ], string='Opciones')
    number = Char('Número')

    def action_import(self):
        if self.action in ['upload_work_order']:
            work_order_obj = self.env['atmsys.work_order']
            work_order_maint_obj = self.env['turei_maintenance.work_order']
            wk_id = work_order_obj.search([('number_new', '=', self.number)])
            if wk_id:
                work_order_id = work_order_obj.browse([wk_id.id])
                if not work_order_maint_obj.search([('number_new', '=', self.number)]):
                    if work_order_id:
                        list_product = []
                        for line in work_order_id.product_order_ids:
                            list_product.append((0, 0, {'product_id': line.product_id.id, 'quantity': line.quantity}))

                        vals = {
                            'code': work_order_id.code,
                            'number_new': work_order_id.number_new,
                            'opening_date': work_order_id.opening_date,
                            'closing_date': work_order_id.closing_date,
                            'execute_cost_center_id': work_order_id.execute_cost_center_id.id,
                            'receive_cost_center_id': work_order_id.receive_cost_center_id.id,
                            'state': work_order_id.state,
                            'creator_id': work_order_id.creator_id.id,
                            'emitter_id': work_order_id.emitter_id.id,
                            'executor_id': work_order_id.executor_id.id,
                            'shutter_id': work_order_id.shutter_id.id,
                            'equipment_or_area': work_order_id.equipment_or_area,
                            'note': work_order_id.note,
                            'product_order_ids': list_product,
                            'description_cancel': work_order_id.description_cancel,
                            'user_cancel_id': work_order_id.user_cancel_id.id,
                            'date_cancel': work_order_id.date_cancel
                        }
                        work_order_maint_id = work_order_maint_obj.create(vals)
                        work_order_id.work_order_mtto_id = work_order_maint_id.id
                else:
                    raise UserError('La Orden de Trabajo ya está registrada en el Módulo Mantenimiento')
            else:
                raise UserError('La Orden de Trabajo solicitada no esta registrada en el Módulo ATM')
        if self.action in ['versat_work_order']:
            connector_id = self.env['db_external_connector.template'].search([('application', '=', 'versat')])
            if connector_id:
                connection = connector_id.connect()
                cursor = connection.cursor()
                query = """SELECT DISTINCT inv_documentoalm.idalmacen, gen_almacen.codigo AS COD_ALMACEN, gen_almacen.nombre AS NOMBRE_ALMACEN
                            FROM inv_documentoentidad INNER JOIN
                              gen_entidad ON inv_documentoentidad.identidad = gen_entidad.identidad INNER JOIN
                              inv_documentocomp ON inv_documentoentidad.iddocumento = inv_documentocomp.iddocumento RIGHT OUTER JOIN
                              inv_movimiento INNER JOIN
                              inv_documento ON inv_movimiento.iddocumento = inv_documento.iddocumento INNER JOIN
                              gen_producto ON inv_movimiento.idproducto = gen_producto.idproducto INNER JOIN
                              inv_concepto ON inv_documento.idconcepto = inv_concepto.idconcepto INNER JOIN
                              inv_inventarioestado ON inv_documento.idestado = inv_inventarioestado.idestado INNER JOIN
                              gen_subsistema ON inv_documento.idsubsistema = gen_subsistema.idsubsistema INNER JOIN
                              gen_medida ON inv_movimiento.idmedida = gen_medida.idmedida ON
                              inv_documentoentidad.iddocumento = inv_documento.iddocumento LEFT OUTER JOIN
                              gen_usuario AS gen_usuario_1 ON inv_documento.idusrconfirmar = gen_usuario_1.idusuario LEFT OUTER JOIN
                              gen_usuario ON inv_documento.idusuario = gen_usuario.idusuario LEFT OUTER JOIN
                              inv_documentoalm INNER JOIN
                              gen_almacen ON inv_documentoalm.idalmacen = gen_almacen.idalmacen ON
                              inv_documento.iddocumento = inv_documentoalm.iddocumento LEFT OUTER JOIN
                              cos_centro INNER JOIN
                              inv_documentogasto ON cos_centro.idcentro = inv_documentogasto.idcentro ON
                              inv_documento.iddocumento = inv_documentogasto.iddocumento LEFT OUTER JOIN
                              inv_documentomlc ON inv_documento.iddocumento = inv_documentomlc.iddocumento LEFT OUTER JOIN
                              inv_movimientomlc ON inv_movimiento.idmovimiento = inv_movimientomlc.idmovimiento FULL OUTER JOIN
                              inv_documentoorden ON inv_documento.iddocumento = inv_documentoorden.iddocumento
                            WHERE(inv_documento.idconcepto IN (36, 51, 57, 60, 61, 62, 79, 81, 83))
                            ORDER BY NOMBRE_ALMACEN"""
                cursor.execute(query)
                rows = cursor.fetchall()