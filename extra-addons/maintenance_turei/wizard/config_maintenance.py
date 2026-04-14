# -*- coding: utf-8 -*-

import logging
from odoo.fields import Selection, Binary, Char
from odoo.models import TransientModel
from odoo.exceptions import UserError

_logger = logging.getLogger('INFO')


class ConfigMaintenance(TransientModel):
    _name = 'maintenance_turei.config_maintenance'
    _description = 'maintenance_turei.config_maintenance'

    action = Selection([('config_maintenance_yes', 'Marcar Ciclo y Fecha (Carga Inicial para el Plan Mtto.)'),
                        ('config_maintenance_no', 'Desmarcar Ciclo y Fecha (Carga Inicial para el Plan Mtto.)'),
                        ('is_industrial', 'Marcar los equipos de Mantenimiento Industrial'),
                        ('maintenance_request_cycle', 'Cargar ciclo a las peticiones de mantenimiento'),
                        ('time_work_order', 'Cargar tiempo al trabajo realizado de las Ord. de Trabajo'),
                        ('upload_maintenance_request', 'Cargar Ciclo de Mantenimiento a las Peticiones')], string='Opciones')
    number = Char('Número')

    def action_import(self):
        equipment_ids = self.env['maintenance.equipment'].search([('is_industrial', '=', True)])
        if self.action in ['config_maintenance_yes']:
            for equip in equipment_ids:
                equip.write({'config_maintenance': True})
        if self.action in ['config_maintenance_no']:
            for equip in equipment_ids:
                equip.write({'config_maintenance': False})
        if self.action in ['is_industrial']:
            for equip in equipment_ids:
                equip.write({'is_industrial': True})
        if self.action in ['maintenance_request_cycle']:
            for equip in equipment_ids:
                for mr in equip.maintenance_ids:
                    cycle = mr.name.split('- ')[1]
                    if cycle:
                        cycle_id = self.env['maintenance_turei.cycle_maintenance'].search([('cycle', '=', cycle), ('equipment_id', '=', equip.id)])
                        mr.cycle_id = cycle_id.id
        if self.action in ['time_work_order']:
            for wk in self.env['maintenance_turei.work_order'].search([]):
                for tr in wk.realized_work_ids:
                    if tr.time:
                        tr.time_hr = float(tr.time)
        if self.action in ['upload_maintenance_request']:
            maint_request_ids = self.env['maintenance.request'].search([('cycle_id', '=', False)])
            cycle_plan_obj = self.env['maintenance_turei.cycle_maintenance_plan']
            for mr in maint_request_ids:
                cycle_id = cycle_plan_obj.search([('equipment_id', '=', mr.equipment_id.id), ('date', '=', mr.request_date)])
                if cycle_id.cycle:
                    mr.cycle_id = cycle_id.cycle
                    mr.name = '{}-{}'.format(mr.equipment_id.code, cycle_id.cycle.cycle)