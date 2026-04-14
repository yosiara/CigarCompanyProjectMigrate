# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _


class ImportConfigWizard(models.Model):
    _name = "import.config.wizard"

    connector_id = fields.Many2one('db_external_connector.template', 'Database', required=True)

    @api.one
    def action_import(self):
        # TODO: Funcion para llamar desde el wizard
        self.action_import_function()
        return True

    @api.model
    def action_import_function(self):
        # TODO: Funcion para llamar desde el cron
        obj = self
        if self._context.get('connector_id'):
            connection = self._context.get('connector_id').connect()
            obj = self.create({'connector_id': self._context.get('connector_id').id})
        else:
            connection = self.connector_id.connect()

        obj.get_modules(connection)
        obj.get_turns(connection)
        obj.get_brigades(connection)
        obj.get_materials(connection)
        obj.get_marcas(connection)
        connection.close()
        return True

    @api.one
    def get_modules(self, connection):
        modules_obj = self.env['hr_sgp_integration.module']

        cursor = connection.cursor()
        cursor.execute("""SELECT id, descripcion
                  FROM cd_modulo
                  WHERE habilitado = True;""")
        modules = cursor.fetchall()

        for row in modules:
            module_data = {}
            module_data['sgp_name'] = row[1]
            module_data['sgp_id'] = row[0]

            ids_modules = modules_obj.search([('sgp_id', '=', row[0]), ('sgp_name', '=', row[1])])
            if len(ids_modules) == 0:
                modules_obj.create(module_data)
            else:
                ids_modules.write(module_data)

        return True

    @api.one
    def get_turns(self, connection):
        turn_obj = self.env['hr_sgp_integration.turn']

        cursor = connection.cursor()
        cursor.execute("""SELECT id, descripcion
                  FROM cd_turno
                  WHERE habilitado = True;""")

        turns = cursor.fetchall()
        for row in turns:
            turn_data = {}
            turn_data['sgp_name'] = row[1]
            turn_data['sgp_id'] = row[0]
            ids_turn = turn_obj.search([('sgp_name', '=', row[1]), ('sgp_id', '=', row[0])])

            if len(ids_turn) == 0:
                turn_obj.create(turn_data)
            else:
                ids_turn.write(turn_data)

        return True

    @api.one
    def get_brigades(self, connection):
        brigade_obj = self.env['hr_sgp_integration.brigade']

        cursor = connection.cursor()
        cursor.execute("""SELECT id, descripcion FROM cd_brigada""")

        brigades = cursor.fetchall()
        for row in brigades:
            brigade_data = {}
            brigade_data['sgp_name'] = row[1]
            brigade_data['sgp_id'] = row[0]
            ids_brigade = brigade_obj.search([('sgp_name', '=', row[1]), ('sgp_id', '=', row[0])])

            if len(ids_brigade) == 0:
                brigade_obj.create(brigade_data)
            else:
                ids_brigade.write(brigade_data)

        return True

    @api.one
    def get_materials(self, connection):
        materials_obj = self.env['hr_sgp_integration.materials']

        cursor = connection.cursor()
        cursor.execute("""SELECT id, descripcion
                  FROM cd_materia_prima;""")

        materials = cursor.fetchall()
        for row in materials:
            materials_data = {}
            materials_data['sgp_name'] = row[1]
            materials_data['sgp_id'] = row[0]
            ids_material = materials_obj.search([('sgp_name', '=', row[1]), ('sgp_id', '=', row[0])])

            if len(ids_material) == 0:
                materials_obj.create(materials_data)
            else:
                ids_material.write(materials_data)

        return True

    @api.one
    def get_marcas(self, connection):
        marcas_obj = self.env['hr_sgp_integration.brand']

        cursor = connection.cursor()
        cursor.execute("""SELECT id, descripcion
                      FROM cd_marca;""")

        marcas = cursor.fetchall()
        for row in marcas:
            marcas_data = {}
            marcas_data['sgp_name'] = row[1]
            marcas_data['sgp_id'] = row[0]
            ids_marcas = marcas_obj.search([('sgp_name', '=', row[1]), ('sgp_id', '=', row[0])])

            if len(ids_marcas) == 0:
                marcas_obj.create(marcas_data)
            else:
                ids_marcas.write(marcas_data)

        return True
