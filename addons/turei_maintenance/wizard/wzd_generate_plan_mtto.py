# -*- coding: utf-8 -*-


from odoo import models, fields, tools, _
from datetime import timedelta, datetime
from odoo.exceptions import ValidationError


class WzdGeneratePlanMtto(models.TransientModel):
    _name = 'wzd.generate.plan.mtto'

    date = datetime.today().date()
    current_year = date.year
    new_year = date.replace(year=current_year + 1).year
    year = fields.Selection(string="Año", selection=[('current', tools.ustr(current_year)), ('new', tools.ustr(new_year))], required=True, default='current')
    category_id = fields.Many2one('maintenance.equipment.category', string='Taller')

    def generate_plan_mtto(self):
        equipment_obj = self.env['maintenance.equipment']
        date = datetime.today().date()
        current_year = date.year
        new_year = date.replace(year=current_year + 1).year

        if self.year == 'current':
            year = current_year
        else:
            year = new_year

        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        if len(incident_plan_obj.search([('year_char', '=', str(year))])) == 0:
            raise ValidationError(_('Error! No hay incidencias registradas para el: %s') % (year))

        # Genera el plan para todos los talleres menos el secundario
        if not self.category_id.is_secundary:
            for equip in equipment_obj.search([('category_id', '=', self.category_id.id), ('is_industrial', '=', True), ('state', 'not in', ['fuera_servicio', 'baja'])]):
                equip.plan_mtto(year)
        else:
            # A partir de aquí es se genera el plan para el taller secundario
            cycle_maint_plan_obj = self.env['turei_maintenance.cycle_maintenance_plan']
            maint_request_obj = self.env['maintenance.request']
            for line in equipment_obj.search([('category_id.is_secundary', '=', True), ('is_industrial', '=', True)], order='line_id'):
                if line.config_maintenance:
                    if len(cycle_maint_plan_obj.search(
                            [('equipment_id', '=', line.id), ('cycle', '=', line.config_cycle.id),
                             ('date', '=', line.config_date)])) == 0:
                        cycle_maint_plan_obj.create({'equipment_id': line.id, 'cycle': line.config_cycle.id,
                                                     'date': line.config_date})
                else:
                    min_date_line = self.min_date_line(cycle_maint_plan_obj, year)
                    cycle_id = min_date_line[0]
                    equip_id = min_date_line[1]
                    date = min_date_line[2]
                    if line.id == equip_id:
                        cycle_ids = line.cycle_maintenance_plan_ids.search([('equipment_id', '=', line.id), ('year_char', '=', str(year)), ('id', '!=', cycle_id)])
                    else:
                        cycle_ids = line.cycle_maintenance_plan_ids.search([('equipment_id', '=', line.id), ('year_char', '=', str(year)), ('date', '!=', date)])
                    for c in cycle_ids:
                        maint_request_obj.search([('equipment_id', '=', self.id), ('request_date', '=', c.date), ('stage_id.done', '=', False)]).unlink()
                    cycle_ids.unlink()

            cond = True
            today = datetime.today().date()
            date_end = today.replace(year=year, month=12, day=31)
            line_obj = self.env['turei_maintenance.line']
            while cond:
                ult_date_line = self.ult_date_line(cycle_maint_plan_obj, year)
                date_ult_mant = ult_date_line[0]
                line_ult_mant = ult_date_line[1]
                cycle_ult_mant = ult_date_line[2]
                new_start_date = self.new_day_mant(date_ult_mant, year)
                if new_start_date <= date_end:
                    domain = []
                    if line_ult_mant.is_module:
                        if line_ult_mant.is_end:
                            sequence = line_obj.search([('is_module', '=', False), ('is_start', '=', True)]).sequence
                            is_module = False
                            cycle_change = True
                        else:
                            sequence = line_ult_mant.sequence + 1
                            is_module = True
                            cycle_change = False
                    else:
                        if line_ult_mant.is_end:
                            if cycle_ult_mant == 'M2':
                                sequence = line_obj.search([('is_module', '=', True), ('is_start', '=', True)]).sequence
                                is_module = True
                                cycle_change = True
                            else:
                                sequence = line_obj.search([('is_module', '=', False), ('is_start', '=', True)]).sequence
                                is_module = False
                                cycle_change = True

                        else:
                            sequence = line_ult_mant.sequence + 1
                            is_module = False
                            cycle_change = False
                    domain.append(('sequence', '=', sequence))
                    domain.append(('is_module', '=', is_module))
                    next_line = line_obj.search(domain)
                    for equip in equipment_obj.search([('category_id.is_secundary', '=', True), ('line_id', '=', next_line.id)]):
                        if cycle_change:
                            if cycle_ult_mant == 'M3':
                                cycle_id = equip.get_cycle_maintenance_id('M2')
                            else:
                                cycle_id = equip.get_cycle_maintenance_id(cycle_ult_mant)
                        else:
                            cycle_id = equip.cycle_maintenance_ids.search([('cycle', '=', cycle_ult_mant), ('equipment_id', '=', equip.id)]).id
                        cycle_maint_plan_obj.create({'equipment_id': equip.id, 'cycle': cycle_id, 'date': new_start_date, 'year_char': str(year)})
                else:
                    cond = False

    def ult_date_line(self, cycle_maint_plan_obj, year):
        today = datetime.today().date()
        date_start = today.replace(year=year, month=1, day=1)
        for line in self.env['maintenance.equipment'].search([('category_id.is_secundary', '=', True)], order='line_id'):
            ultim_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', line.id), ('year_char', '=', str(year))],
                                                      order='date desc', limit=1)
            if ultim_cycle and ultim_cycle.date:
                if datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date() > date_start:
                    date_start = datetime.strptime(ultim_cycle.date, '%Y-%m-%d').date()
                    li = line.line_id
                    cycle = ultim_cycle.cycle.cycle
        return date_start, li, cycle

    def min_date_line(self, cycle_maint_plan_obj, year):
        today = datetime.today().date()
        date_start = today.replace(year=year, month=12, day=31)
        for line in self.env['maintenance.equipment'].search([('category_id.is_secundary', '=', True)], order='line_id'):
            primer_cycle = cycle_maint_plan_obj.search([('equipment_id', '=', line.id), ('year_char', '=', str(year))],
                                                      order='date asc', limit=1)
            if primer_cycle and primer_cycle.date:
                if datetime.strptime(primer_cycle.date, '%Y-%m-%d').date() < date_start:
                    date_start = datetime.strptime(primer_cycle.date, '%Y-%m-%d').date()
                    equip_id = line.id
                    cycle_plan_id = primer_cycle.id
        return cycle_plan_id, equip_id, date_start

    def new_day_mant(self, date_ult_mant, year):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        cond = True
        new_start_date = date_ult_mant + timedelta(days=7)
        # new_end_date = new_start_date + timedelta(days=4)
        while cond:
            # incident_plan_i = incident_plan_obj.search(
            #     [('year_char', '=', str(year)), ('date_start', '<=', new_start_date),
            #      ('date_end', '>=', new_start_date)])
            #
            # if len(incident_plan_i) == 0:
            #     cond = False
            # else:
            #     new_start_date = new_start_date + timedelta(days=7)
                # new_end_date = new_start_date + timedelta(days=4)
            ban = self.validate_date(new_start_date, year)
            if not ban:
                cond = False
            else:
                new_start_date = new_start_date + timedelta(days=7)
        return new_start_date

    def validate_date(self, date, year):
        incident_plan_obj = self.env['turei_maintenance.incident_plan']
        ban = False
        for i in range(0, 4):
            date_new = date + timedelta(days=i)
            incident_plan_i = incident_plan_obj.search(
                [('year_char', '=', str(year)), ('date_start', '<=', date_new),
                 ('date_end', '>=', date_new)])
            if len(incident_plan_i) > 0:
                ban = True
        return ban
