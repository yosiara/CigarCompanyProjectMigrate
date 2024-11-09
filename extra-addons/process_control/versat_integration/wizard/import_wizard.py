# -*- coding: utf-8 -*-

import logging

import datetime
from datetime import datetime
from odoo import api
from odoo.fields import Many2one, Selection, Date, Boolean, Many2many
from odoo.models import TransientModel
from odoo.tools import ustr

_logger = logging.getLogger('INFO')

options = [
    ('only_new_products', 'Update product list...'),
    ('update_all_products', 'Update all products...'),
    ('specific_product', 'Update specific product...'),
    ('warehouses', 'Update warehouses...'),
    ('specific_product_movements', 'Update specific product movements...'),
    ('synchronize_product_movements', 'Synchronize specific product movements'),
    ('action_update_all_product_movementes', 'Actualizar movimientos de productos y sus existencias...'),
    ('action_import_accounts', 'Importar cuentas...'),
]


class ImportWizard(TransientModel):
    _name = 'versat.import_wizard'
    _description = 'versat.import_wizard'

    def _get_date_to_limit(self):
        return datetime(year=2018, month=1, day=1).date()

    connector_id = Many2one('db_external_connector.template', string='Database', required=True)
    action = Selection(options, default='only_new_products', string='Import')

    # Used when it's necessary update only the information of an specific product...
    product_id = Many2one('simple_product.product', string='Product')

    # Used when the initial data import has not been accomplished to start of year,
    # and the movements occurred by "Out Vouchers" have not been used in out-in operations...
    limit_operations = Boolean(string='Limit operations?')
    date_to_limit = Date(string='Date', default=_get_date_to_limit, readonly=True)


    import_after_specified_date = Boolean(string='Import after specified date?')
    date = Date()

    @api.onchange('action', 'connector_id')
    def _on_change_action(self):
        if self.action and self.connector_id and self.action == 'specific_product_movements':
            connection = self.connector_id.connect()
            cursor = connection.cursor()

            query = """SELECT idconcepto, idregdocum, idcriterio, codigo, descripcion, idcategoria, Activo
                       FROM inv_concepto;"""

            concept_obj = self.env['versat.concept']
            concepts = concept_obj.search([])

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                values = {
                    'idconcepto': row[0],
                    'idregdocum': row[1],
                    'idcriterio': row[2],
                    'codigo': row[3],
                    'description': row[4],
                    'idcategoria': row[5],
                    'activo': row[6],
                    'to_import': False,
                    'is_out_operation': True if row[0] in [36, 50, 51, 57, 61, 62, 83, 92, 94, 95, 97, 98, 99, 100, 101, 121] else False
                }

                recs = concepts.filtered(lambda r: r.idconcepto == row[0])
                if recs:
                    values.pop('idconcepto')
                    values.pop('to_import')
                    #values.pop('is_out_operation')
                    recs[0].write(values)
                else:
                    concept_obj.create(values)

            connection.close()
            self.concept_ids = concept_obj.search([])

    def action_import(self):
        #_logger.info("-------------------------------------------------")
        #product_obj = self.env['simple_product.product']
        #product_control_obj = self.env['warehouse.product_control']
        #products = product_obj.search([])
        #_logger.info("Comenzando ciclo...")
        #for product in products:
        #    product_control = product_control_obj.search([('product_id', '=', product.id)], limit=1)
        #    product_control.write({'quantity_system': product.total})
        #    _logger.info("Updated stock of product: %s" % (product.id))
        #return True
        
        if self.action in ['only_new_products', 'update_all_products', 'specific_product']:
            return self.action_import_products()
        elif self.action in ['warehouses']:
            return self.action_import_warehouses()
        elif self.action in ['specific_product_movements']:
            return self.action_update_product_movements()
        elif self.action in ['synchronize_product_movements']:
            return self.action_synchronize_product_movements()
        elif self.action in ['action_update_all_product_movementes']:
            return self.action_update_all_product_movementes();
        elif self.action == 'action_import_accounts':
            return self.action_import_accounts()

    def action_import_accounts(self):
        connection = self.connector_id.connect()
        cursor = connection.cursor()

        account_obj = self.env['versat_integration.account']
        accounts = account_obj.search([])
        account_dict = {}

        for account in accounts:
            account_dict[account.external_id] = account.id

        query = "SELECT idcuenta, clave, descripcion, naturaleza FROM con_cuentanat;"
        cursor.execute(query)

        for row in cursor:
            code = row[1]
            if len(code) == 3:
                values = {'external_id': int(row[0]), 'code': int(code), 'name': ustr(row[2])}
                if not account_dict.get(row[0], False):
                    res = account_obj.create(values)
                    account_dict[res.external_id] = res.id
                else:
                    values.pop('external_id')
                    recs = accounts.filtered(lambda r: r.external_id == row[0])
                    if recs:
                        recs[0].write(values)

                _logger.info("Processed account: %s." % (code,))

        connection.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('versat_integration.versat_integration_account_menu_item').id},
        }

    def action_import_products(self):
        connection = self.connector_id.connect()
        cursor = connection.cursor()

        # Importing warehouses...
        warehouse_obj = self.env['warehouse.warehouse']
        warehouses = warehouse_obj.search([])
        warehouse_dict = {}

        for warehouse in warehouses:
            warehouse_dict[warehouse.external_id] = warehouse.id

        query = "SELECT idalmacen, codigo, nombre FROM gen_almacen WHERE activo = 1;"
        cursor.execute(query)

        for row in cursor:
            values = {
                'external_id': row[0],
                'code': row[1],
                'name': ustr(row[2])
            }

            if not warehouse_dict.get(row[0], False):
                res = warehouse_obj.create(values)
                warehouse_dict[res.external_id] = res.id
            else:
                values.pop('external_id')
                recs = warehouses.filtered(lambda r: r.external_id == row[0])
                if recs:
                    recs[0].write(values)

        # Importing unit of measure...
        versat_uom_obj = self.env['versat.uom']
        versat_uom_list = versat_uom_obj.search([])

        versat_uom_dict = {}
        for versat_uom in versat_uom_list:
            versat_uom_dict[versat_uom.external_id] = (versat_uom.id, versat_uom.uom_id.id)

        query = "SELECT idmedida, clave, descripcion FROM gen_medida;"
        cursor.execute(query)

        for row in cursor:
            values = {
                'name': ustr(row[1]),
                'external_id': row[0],
                'description': ustr(row[2])
            }

            if not versat_uom_dict.get(row[0], False):
                res = versat_uom_obj.create(values)
                versat_uom_dict[res.external_id] = (res.id, res.uom_id.id)
            else:
                recs = versat_uom_list.filtered(lambda r: r.external_id == row[0])
                recs[0].write(values)

        # Importing product's categories...
        category_obj = self.env['product.category']
        categories = category_obj.search([])

        category_dict = {}
        for cat in categories:
            category_dict[cat.external_id] = cat.id

        query = "SELECT idcategoria, nombre FROM inv_categoria;"
        cursor.execute(query)

        for row in cursor:
            if not category_dict.get(row[0], False):
                res = category_obj.create({'name': ustr(row[1]), 'external_id': row[0]})
                category_dict[res.external_id] = res.id
            else:
                recs = categories.filtered(lambda r: r.external_id == row[0])
                recs[0].write({'name': ustr(row[1])})

        # Loading accounts references...
        account_obj = self.env['versat_integration.account']
        accounts = account_obj.search([])
        account_dict = {}

        for account in accounts:
            account_dict[account.external_id] = account.id

        # Importing products...
        location_obj = self.env['warehouse.product.location']
        product_obj = self.env['simple_product.product']
        products = []

        if self.action == 'specific_product':
            products = product_obj.search([('id', '=', self.product_id.id)])
        else:
            products = product_obj.search([])

        products.write({'is_new': False})
        product_dict, product_list = {}, []

        for product in products:
            product_dict[product.external_id] = product.id
            product_list.append(product.external_id)

        group_dict = {}
        group_obj = self.env['simple_product.product.group']
        groups = group_obj.search([])

        for group in groups:
            group_dict[group.code] = group.id

        query = """SELECT p.idproducto, p.codigo, p.descripcion, e.idmedida, e.preciomn, e.preciomlc, e.idcategoria,
                          e.ubicacion, ea.idalmacen, account.idcuenta
                   FROM gen_producto p
                   INNER JOIN gen_nivelclasprod nc ON p.idnivelclas = nc.idnivelclas
                   INNER JOIN inv_existencia e ON (p.idproducto = e.idproducto)
                   INNER JOIN gen_medida m ON e.idmedida = m.idmedida
                   INNER JOIN inv_categoria c ON e.idcategoria = c.idcategoria
                   INNER JOIN inv_existenciaalm ea ON e.idexistencia = ea.idexistencia
                   INNER JOIN con_cuenta cuenta ON cuenta.idcuenta = e.idcuentamn
                   INNER JOIN con_cuentanat as account on cuenta.idcuenta = account.idcuenta"""

        if self.action == 'only_new_products' and len(product_list):
            query += " WHERE p.idproducto > " + str(product_list[-1]) + ";"
        elif self.action == 'specific_product':
            query += " WHERE p.idproducto = " + str(self.product_id.external_id) + ";"

        cursor.execute(query)

        for row in cursor:
            if row[1] in ['0011009629']:
                continue

            values = {
                'external_id': row[0],
                'code': row[1],
                'name': ustr(row[2]),
                'uom_id': versat_uom_dict.get(row[3])[1],
                'price': row[4],
                'price_extra': row[5],
                'category_id': category_dict.get(row[6], False),
                'account_id': account_dict.get(row[9], False)
            }

            group_code = row[7].split('-')
            group_code = group_code[1] if len(group_code) >= 2 else False

            if group_code:
                group_id = group_dict.get(group_code, False)
                if group_id:
                    values['group_id'] = group_id

            if not product_dict.get(row[0], False):
                res = product_obj.create(values)
                product_dict[res.external_id] = res.id

                location_obj.create({
                    'product_id': res.id,
                    'location': ustr(row[7]),
                    'warehouse_id': warehouse_dict[row[8]],
                })

                _logger.info("Imported product: %s." % (row[0],))

            else:
                values.pop('external_id')
                #recs = products.filtered(lambda r: r.external_id == row[0])
                recs = product_obj.search([('external_id', '=', row[0])])

                if recs:
                    recs[0].write(values)
                    has_location = False

                    for location in recs[0].location_ids:
                        if location.warehouse_id.id == warehouse_dict[row[8]]:
                            location.write({'location': ustr(row[7])})
                            has_location = True

                    if not len(recs[0].location_ids) or not has_location:
                        location_obj.create({
                            'product_id': recs[0].id,
                            'location': ustr(row[7]),
                            'warehouse_id': warehouse_dict[row[8]],
                        })

                    _logger.info("Updated product: %s." % (row[0],))

        connection.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('simple_product.simple_product_product_root_menu').id},
        }

    def action_import_warehouses(self):
        connection = self.connector_id.connect()
        cursor = connection.cursor()

        warehouse_obj = self.env['warehouse.warehouse']
        warehouses = warehouse_obj.search([])

        warehouse_dict = {}
        for warehouse in warehouses:
            warehouse_dict[warehouse.external_id] = warehouse.id

        # Importing product movements...
        transference_obj = self.env['versat_integration.product_movement']
        product_control_obj = self.env['warehouse.product_control']
        product_obj = self.env['simple_product.product']
        products = product_obj.search([])

        concept_obj = self.env['versat.concept']
        concepts_out = concept_obj.search([('is_out_operation', '=', True)])
        concepts_out_external_ids = [x.idconcepto for x in concepts_out]

        concepts_to_use = concept_obj.search([('to_import', '=', True)])
        concepts_to_use_external_ids = [x.idconcepto for x in concepts_to_use]

        for product in products:
            query = """
                SELECT idmovimiento, cantidad, reg_doc.tipo, doc_x_alm.idalmacen, doc.fecha, conc.idconcepto, conc.descripcion
                FROM inv_movimiento as mov
                INNER JOIN inv_documento as doc on mov.iddocumento = doc.iddocumento
                INNER JOIN inv_documentoalm as doc_x_alm ON doc.iddocumento = doc_x_alm.iddocumento
                INNER JOIN inv_concepto as conc ON doc.idconcepto = conc.idconcepto
                INNER JOIN inv_regdocum as reg_doc on conc.idregdocum = reg_doc.idregdocum
                WHERE idproducto = '%s'"""

            if self.import_after_specified_date:
                query += "AND doc.fecha >= '%s'"

            query += " ORDER BY doc.fecha DESC;"
            if self.import_after_specified_date:
                query = query % (product.external_id, self.date)
            else:
                query = query % (product.external_id,)

            cursor.execute(query)
            rows = cursor.fetchall()

            for row in rows:
                warehouse_id = warehouse_dict[row[3]]
                qty = row[1]

                values = {
                    'external_id': row[0],
                    'product_id': product.id,
                    'type': 'in' if row[2] == 1 else 'out',
                    'warehouse_id': warehouse_id,
                    'quantity': round(qty, 4),
                    'description': ustr(row[6]),
                    'date': row[4],
                    'movement_concept': row[5]
                }

                # Creating Movement and Updating product stock...
                if not len(transference_obj.search([('external_id', '=', row[0])])):
                    if self.limit_operations:
                        _date = self.date_to_limit.split('-')
                        _date = datetime.datetime(int(_date[0]), int(_date[1]), int(_date[2]))

                    if self.limit_operations and row[4] >= _date and row[3] not in ['02', '06', '07', '08', '10', '11']:
                        if row[5] in concepts_to_use_external_ids:
                            transference_obj.create(values)
                    else:
                        transference_obj.create(values)

                    product_control = product_control_obj.search(
                        [('warehouse_id', '=', warehouse_id), ('product_id', '=', product.id)]
                    )

                    if not product_control:
                        values = {
                            'warehouse_id': warehouse_id,
                            'product_id': product.id,
                            'quantity_system': round(qty, 4),
                            'quantity': round(qty, 4)
                        }

                        if self.limit_operations and row[4] >= _date and row[3] not in ['02', '06', '07', '08', '10', '11']:
                            if row[5] in concepts_to_use_external_ids:
                                product_control_obj.create(values)
                                _logger.info("Created stock of product: %s, warehouse: %s" % (product.external_id, warehouse_id))
                        else:
                            product_control_obj.create(values)
                            _logger.info("Created stock of product: %s, warehouse: %s" % (product.external_id, warehouse_id))
                    else:
                        if row[2] == 1:
                            quantity = product_control.quantity + round(qty, 4)
                            quantity_system = product_control.quantity_system + round(qty, 4)
                        else:
                            quantity = product_control.quantity - round(qty, 4)
                            quantity_system = product_control.quantity_system - round(qty, 4)

                        values = {'quantity': quantity}
                        if self.limit_operations and row[4] >= _date:
                            if row[5] in concepts_to_use_external_ids:
                                values['quantity_system'] = quantity_system
                        else:
                            values['quantity_system'] = quantity_system

                        product_control.write(values)
                        _logger.info("Updated stock of product: %s, warehouse: %s" % (product.external_id, warehouse_id))

            _logger.info("Imported movements of product %s." % (product.external_id,))
            self._cr.commit()

        connection.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('versat_integration.versat_integration_product_movement_menu_item').id}
        }

    def action_update_all_product_movementes(self):
        product_obj = self.env['simple_product.product']
        products = product_obj.search([], order='name desc')
        for product in products:
            self.action_update_product_movements(product, True)
            self._cr.commit()
        # return True
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('versat_integration.versat_integration_product_movement_menu_item').id}
        }
        

    def action_update_product_movements(self, product=None, noreturn=False):
        _product = product
        if not _product:
            _product = self.product_id
        
        warehouse_obj = self.env['warehouse.warehouse']
        warehouses = warehouse_obj.search([])

        warehouse_dict = {}
        for warehouse in warehouses:
            warehouse_dict[warehouse.external_id] = warehouse.id

        concept_obj = self.env['versat.concept']
        concepts_to_use = concept_obj.search([('to_import', '=', True)])
        concepts_to_use_external_ids = [x.idconcepto for x in concepts_to_use]

        connection = self.connector_id.connect()
        cursor = connection.cursor()

        product_movement_obj = self.env['versat_integration.product_movement']
        transference_obj = self.env['versat_integration.product_movement']
        product_control_obj = self.env['warehouse.product_control']

        _logger.info("**************************************************************************************************")
        _logger.info("Borrando movimientos del product: %s, pR volver a cargarlos!!!" % (_product.code,))
        movements = product_movement_obj.search([('product_id', '=', _product.id)])
        movements.unlink()

        product_controls = product_control_obj.search([('product_id', '=', _product.id)])
        product_controls.write({'quantity_system': 0.0, 'quantity': 0.0})
        _logger.info("**************************************************************************************************")
        _logger.info("Updated stock of product: %s.!!!" % (_product.code,))

        query = """
            SELECT idmovimiento, cantidad, reg_doc.tipo, doc_x_alm.idalmacen, doc.fecha, conc.idconcepto, conc.descripcion
            FROM inv_movimiento as mov
            INNER JOIN inv_documento as doc on mov.iddocumento = doc.iddocumento
            INNER JOIN inv_documentoalm as doc_x_alm ON doc.iddocumento = doc_x_alm.iddocumento
            INNER JOIN inv_concepto as conc ON doc.idconcepto = conc.idconcepto
            INNER JOIN inv_regdocum as reg_doc on conc.idregdocum = reg_doc.idregdocum
            WHERE idproducto = '%s' ORDER BY doc.fecha;"""

        query = query % (_product.external_id,)
        cursor.execute(query)
        rows = cursor.fetchall()

        if self.limit_operations:
            _date = self.date_to_limit.split('-')
            _date = datetime.datetime(int(_date[0]), int(_date[1]), int(_date[2]))

        for row in rows:
            warehouse_id = warehouse_dict[row[3]]
            qty = row[1]

            values = {
                'external_id': row[0],
                'product_id': _product.id,
                'type': 'in' if row[2] == 1 else 'out',
                'warehouse_id': warehouse_id,
                'quantity': round(qty, 4),
                'description': ustr(row[6]),
                'date': row[4]
            }

            # Creating Movement and Updating product stock...
            if not len(transference_obj.search([('external_id', '=', row[0])])):
                if self.limit_operations and row[4] >= _date:
                    if row[5] in concepts_to_use_external_ids:
                        transference_obj.create(values)
                else:
                    transference_obj.create(values)

                product_control = product_control_obj.search(
                    [('warehouse_id', '=', warehouse_id), ('product_id', '=', _product.id)]
                )

                if not product_control:
                    values = {
                        'warehouse_id': warehouse_id,
                        'product_id': _product.id,
                        'quantity_system': round(qty, 4),
                        'quantity': round(qty, 4)
                    }

                    if self.limit_operations and row[4] >= _date:
                        if row[5] in concepts_to_use_external_ids:
                            product_control_obj.create(values)
                            _logger.info("Created stock of product: %s, warehouse: %s" % (_product.external_id, warehouse_id))
                    else:
                        product_control_obj.create(values)
                        _logger.info("Created stock of product: %s, warehouse: %s" % (_product.external_id, warehouse_id))
                else:
                    if row[2] == 1:
                        quantity = product_control.quantity + round(qty, 4)
                        quantity_system = product_control.quantity_system + round(qty, 4)
                    else:
                        quantity = product_control.quantity - round(qty, 4)
                        quantity_system = product_control.quantity_system - round(qty, 4)

                    values = {'quantity': quantity}
                    if self.limit_operations and row[4] >= _date:
                        if row[5] in concepts_to_use_external_ids:
                            values['quantity_system'] = quantity_system
                    else:
                        values['quantity_system'] = quantity_system

                    product_control.write(values)
                    _logger.info("Updated stock of product: %s, warehouse: %s" % (_product.external_id, warehouse_id))

        product_order_obj = self.env['warehouse.product_order']
        for product_control in product_controls:
            product_orders = product_order_obj.search([('product_id', '=', _product.id), ('warehouse_id', '=', product_control.warehouse_id.id)])
            for order in product_orders:
                product_control.write({'quantity_system': product_control.quantity_system - order.quantity})

        connection.close()
        if not noreturn:
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
                'params': {'menu_id': self.env.ref('versat_integration.versat_integration_product_movement_menu_item').id}
            }

    def action_synchronize_product_movements(self):
        connection = self.connector_id.connect()
        cursor = connection.cursor()

        query = """
            SELECT idmovimiento
            FROM inv_movimiento as mov
            INNER JOIN inv_documento as doc on mov.iddocumento = doc.iddocumento
            INNER JOIN inv_documentoalm as doc_x_alm ON doc.iddocumento = doc_x_alm.iddocumento
            INNER JOIN inv_concepto as conc ON doc.idconcepto = conc.idconcepto
            INNER JOIN inv_regdocum as reg_doc on conc.idregdocum = reg_doc.idregdocum
            WHERE idproducto = '%s';"""

        query = query % (self.product_id.external_id,)
        cursor.execute(query)
        rows = cursor.fetchall()
        movements_external_ids = [x[0] for x in rows]

        versat_product_mov_obj = self.env['versat_integration.product_movement']
        versat_product_movements = versat_product_mov_obj.search([('product_id', '=', self.product_id.id)])

        for versat_product_mov in versat_product_movements:
            if versat_product_mov.external_id not in movements_external_ids:
                versat_product_mov.unlink()

        connection.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('versat_integration.versat_integration_product_movement_menu_item').id}
        }

    # Esta funcion solo la voy a usar para actualizar la descripcion de los movimientos...
    def action_update_movement_description(self):
        versat_product_mov_obj = self.env['versat_integration.product_movement']
        versat_product_movements = versat_product_mov_obj.search([])

        query = """
            SELECT conc.descripcion
            FROM inv_movimiento as mov
            INNER JOIN inv_documento as doc on mov.iddocumento = doc.iddocumento
            INNER JOIN inv_documentoalm as doc_x_alm ON doc.iddocumento = doc_x_alm.iddocumento
            INNER JOIN inv_concepto as conc ON doc.idconcepto = conc.idconcepto
            INNER JOIN inv_regdocum as reg_doc on conc.idregdocum = reg_doc.idregdocum
            WHERE idmovimiento = '%s';"""

        connection = self.connector_id.connect()
        cursor = connection.cursor()

        for versat_product_mov in versat_product_movements:
            cursor.execute(query % (versat_product_mov.external_id,))
            row = cursor.fetchone()

            versat_product_mov.description = ustr(row[0])
            _logger.info("Updated movement: %s." % (versat_product_mov.external_id,))

        connection.close()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('versat_integration.versat_integration_product_movement_menu_item').id}
        }
ImportWizard()
