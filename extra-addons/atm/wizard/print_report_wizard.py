# -*- coding: utf-8 -*-

import cStringIO
import datetime
import xlwt
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools import ustr
from xlwt import *
from ..models.styles import *
from odoo.addons.atm.models.utils import months_number_dict, months, number_months_dict


class PrintReportWizard(models.TransientModel):
    _name = 'atm.print_report_wizard'
    _description = 'atm.print_report_wizard'

    def _default_get_year(self):
        return fields.Date.from_string(fields.Date.context_today(self)).strftime('%Y')

    @api.model
    def _get_default_month(self):
        return months_number_dict[fields.Date.today().split('-')[1]]

    month = fields.Selection(months, default=_get_default_month)
    year = fields.Char(size=4, required=True, default=_default_get_year)

    report_name = fields.Selection([
        ('report_one', 'Parte de existencias y coverturas de materiales fundamentales.'),
        ('report_two', 'Parte de gastables.'),
        ('report_three', 'Parte de compras, ventas y consumo de materiales seleccionados.'),
        ('report_four', 'Informe de cumplimiento de entregas de materiales fundamentales.'),
        ('report_five', 'Parte de materiales fundamentales y gastables críticos.'),
        ('report_six', 'Parte de entrada de materiales.'),
        ('report_seven', 'Parte de extracciones de recursos de la UEB IST.')
    ], string='Informe', required=True, default='report_one'
    )

    @api.model
    def get_filename(self):
        return 'excel_document.xls'

    def get_file(self):
        if self.report_name == 'report_one':
            return self.report_one()

        if self.report_name == 'report_two':
            return self.report_two()

        if self.report_name == 'report_three':
            return self.report_three()

        if self.report_name == 'report_four':
            return self.report_four()

        if self.report_name == 'report_five':
            return self.report_five()

        if self.report_name == 'report_six':
            return self.report_six()

        if self.report_name == 'report_seven':
            return self.report_seven()

    @api.model
    def report_one(self):
        workbook = Workbook()
        worksheet = workbook.add_sheet('Page1')

        current_month = datetime.date(int(self.year), int(number_months_dict[self.month]), 10)
        next_month = current_month + relativedelta(months=1)
        third_month = next_month + relativedelta(months=1)

        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 0, 1, ustr('PRODUCCIÓN / MESES'), _format)
        worksheet.write(0, 2, current_month.strftime('%b').upper(), _format)
        worksheet.write(0, 3, next_month.strftime('%b').upper(), _format)
        worksheet.write(0, 4, third_month.strftime('%b').upper(), _format)
        worksheet.write(0, 5, 'TOTAL', _format)

        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1, top 1; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 6, 8, ustr('MINISTERIO DE LA AGRICULTURA'), _format)

        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(1, 1, 6, 8, ustr('EMP. CIGARROS "LÁZARO PEÑA"'), _format)
        worksheet.write_merge(2, 2, 6, 8, ustr('HOLGUÍN'), _format)
        worksheet.write_merge(3, 3, 6, 8, ustr(''), _format)

        _format = xlwt.easyxf(
            "font: height 0x00F0; borders: right 1, left 1; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(4, 6, 6, 8, ustr('PARTE DIARIO DE MATERIALES FUNDAMENTALES'), _format)
        worksheet.write_merge(7, 7, 6, 8, fields.Date.today(), xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1; font: bold on; align: wrap on, horiz center, vert center"))

        product_destinies, x = self.env['atm.product_destiny'].search([]), 1
        plan_record_cls = self.env['atm.plan_record']

        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        for rec in product_destinies:
            worksheet.write_merge(x, x, 0, 1, rec.name, style_justified_normal)
            plan01 = plan_record_cls.search([('destiny_id', '=', rec.id), ('plan_id.year', '=', self.year)])
            plan02 = plan_record_cls.search([('destiny_id', '=', rec.id), ('plan_id.year', '=', next_month.year)])
            plan03 = plan_record_cls.search([('destiny_id', '=', rec.id), ('plan_id.year', '=', third_month.year)])

            plan1 = getattr(plan01, 'plan%s' % (current_month.strftime('%m'),), 0.0)
            plan2 = getattr(plan02, 'plan%s' % (next_month.strftime('%m'),), 0.0)
            plan3 = getattr(plan03, 'plan%s' % (third_month.strftime('%m'),), 0.0)

            worksheet.write(x, 2, plan1, _format)
            worksheet.write(x, 3, plan2, _format)
            worksheet.write(x, 4, plan3, _format)
            worksheet.write(x, 5, plan1 + plan2 + plan3, _format)
            x += 1

        x += 1
        conf = self.env['atm.report_configuration'].search([], limit=1)
        products = conf.report_one_product_ids

        # Para evaluar las formulas del plan diario...
        general_plan, dict_values = self.env['atm.production_plan'].search([('year', '=', self.year)]), {}
        for record in general_plan.record_ids:
            dict_values[record.destiny_id.code] = getattr(record, 'plan%s' % (current_month.strftime('%m'),), 0.0)


        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        _format_left = xlwt.easyxf("borders: right 1, left 1, top 1, bottom 1; align: vert center")

        worksheet.write(x, 0, 'No.', _format_header)
        worksheet.write(x, 1, ustr('Descripción del producto'), _format_header)
        worksheet.write(x, 2, 'U/M', _format_header)
        worksheet.write(x, 3, 'PROC', _format_header)
        worksheet.write(x, 4, ustr('Norma consumo'), _format_header)
        worksheet.write(x, 5, 'Inventario', _format_header)
        worksheet.write(x, 6, 'Cobertura real en millones de cig.', _format_header)
        worksheet.write(x, 7, ustr('Cobertura en días según plan del mes'), _format_header)
        worksheet.write(x, 8, ustr('Plan diario a fabricar con cada producto'), _format_header)
        x += 1

        groups = []
        for item in conf.report_one_product_ids:
            product = item.product_id
            if product.group_number in groups:
                continue

            _products = conf.report_one_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            e, f = float(product.get_consumption_norm(item.uom_id.id)), 0.0
            # f = float(product.total * product.conversion_factor)
            for _p in _products:
                f += float(_p.product_id.total * _p.product_id.conversion_factor)
            g = float(f / e) if e != 0 else 0.0

            worksheet.write(x, 0, ustr(product.group_number), _format_center)
            worksheet.write(x, 1, ustr(product.group_name), style_justified_normal)
            worksheet.write(x, 2, ustr(item.uom_id.name), _format_center)
            worksheet.write(x, 3, 'NAC' if product.origin == 'national' else 'IMP', _format_center)
            worksheet.write(x, 4, e, _format_left)
            worksheet.write(x, 5, round(f, 1), _format_left)
            worksheet.write(x, 6, round(g, 1), _format_left)

            daily_plan = 0.0
            if product.formula_month_plan:
                daily_plan = eval(product.formula_month_plan, dict_values)

            dp = float(daily_plan) / conf.working_days if conf.working_days != 0.0 else 0.0
            coverage_in_days = (g / dp) if dp > 0 else 0.0
            is_critic = True if (product.origin == 'national' and coverage_in_days < 30 and product.destiny_id.code in [
                'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'national' and g < 30 and product.destiny_id.code in ['A']) or (
                                    product.origin == 'international' and coverage_in_days < 90 and product.destiny_id.code in [
                                        'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'international' and g < 90 and product.destiny_id.code in [
                                        'A']) else False
            worksheet.write(x, 7, round(coverage_in_days, 1), style_warning if is_critic else _format_left)
            worksheet.write(x, 8, round(dp, 1), _format_left)

            groups.append(product.group_number)
            x += 1

        # Section: Other important products...
        x += 1
        _format = xlwt.easyxf("font: bold on, colour_index 0x7CCC; align: vert center;")
        worksheet.write(x, 0, 'Otros materiales importantes'.upper(), _format)
        worksheet.gridline_colour_index = 0x40 + 10

        other_products = conf.report_one_other_product_ids
        _format = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center;")
        x += 1

        if len(other_products):
            worksheet.write(x, 0, 'No.', _format_header)
            worksheet.write(x, 1, ustr('Descripción del producto'), _format_header)
            worksheet.write(x, 2, 'U/M', _format_header)
            worksheet.write(x, 3, 'PROC', _format_header)
            worksheet.write(x, 4, ustr('Norma consumo'), _format_header)
            worksheet.write(x, 5, 'Inventario', _format_header)
            worksheet.write(x, 6, 'Cobertura real', _format_header)
            worksheet.write(x, 7, ustr('Cobertura en días según plan del mes'), _format_header)
            worksheet.write(x, 8, ustr('Plan diario de producción'), _format_header)
            worksheet.row(x).height = 0x0d00 + 20
            x += 1

            for rec in other_products:
                product = rec.product_id
                e = float(product.get_consumption_norm(rec.uom_id.id))
                f = float(product.total * product.conversion_factor)
                if product.code == '0004001184':
                    f -= 11.88
                g = float(f / e) if e != 0 else 0.0

                worksheet.write(x, 0, ustr(product.group_number), style_center_normal)
                worksheet.write(x, 1, ustr(product.name), style_justified_normal)
                worksheet.write(x, 2, ustr(rec.uom_id.name), style_center_normal)
                worksheet.write(x, 3, 'NAC' if product.origin == 'national' else 'IMP', style_center_normal)
                worksheet.write(x, 4, e, _format_left)
                worksheet.write(x, 5, round(f, 1), _format_left)
                worksheet.write(x, 6, round(g, 1), _format_left)

                daily_plan = 0.0
                if product.formula_month_plan:
                    daily_plan = eval(product.formula_month_plan, dict_values)

                dp = float(daily_plan) / conf.working_days if conf.working_days != 0.0 else 0.0
                coverage_in_days = (g / dp) if dp > 0 else 0.0
                is_critic = True if (
                                        product.origin == 'national' and coverage_in_days < 30 and product.destiny_id.code in [
                                            'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                        product.origin == 'national' and g < 30 and product.destiny_id.code in [
                                            'A']) or (
                                        product.origin == 'international' and coverage_in_days < 90 and product.destiny_id.code in [
                                            'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                        product.origin == 'international' and g < 90 and product.destiny_id.code in [
                                            'A']) else False
                worksheet.write(x, 7, round(coverage_in_days, 1), style_warning if is_critic else _format_left)
                worksheet.write(x, 8, round(dp, 1), _format_left)
                x += 1

        # Columns width...
        worksheet.col(1).width = 0x0d00 + 8000
        worksheet.col(5).width = 0x0d00 + 1300
        worksheet.col(6).width = 0x0d00 + 1300
        worksheet.col(7).width = 0x0d00 + 1300
        worksheet.col(8).width = 0x0d00 + 1300

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_two(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Parte Diario')
        worksheet1 = workbook.add_sheet('Parte Dir General')
        fecha_last_day = datetime.datetime.now().date() - datetime.timedelta(days=1)

        _format = xlwt.easyxf("font: height 0x00B4; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 0, 12,
                              ustr('EMPRESA DE CIGARROS "LÁZARO PEÑA" U.E.B. COMERCIALIZACIÓN Y ABASTECIMIENTO'),
                              _format)
        worksheet1.write_merge(0, 0, 0, 7,
                              ustr('EMPRESA DE CIGARROS "LÁZARO PEÑA" U.E.B. COMERCIALIZACIÓN Y ABASTECIMIENTO'),
                              _format)
        worksheet.write_merge(1, 1, 0, 12, ustr('EXISTENCIA Y COBERTURA DE PIEZAS DE RÁPIDO DESGASTE'), _format)
        worksheet1.write_merge(1, 1, 0, 7, ustr('EXISTENCIA Y COBERTURA DE PIEZAS DE RÁPIDO DESGASTE'), _format)
        worksheet.write_merge(2, 2, 0, 12, ustr('FECHA: ' + str(fecha_last_day)), _format)
        worksheet1.write_merge(2, 2, 0, 7, ustr('FECHA: ' + str(fecha_last_day)), _format)

        destiny = 0
        x = 3
        y = 4
        conf = self.env['atm.report_configuration'].search([], limit=1)
        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")

        worksheet1.write(4, 0, ustr('No.'), _format_header)
        worksheet1.write(4, 1, ustr('DENOMINACIÓN DE LA PIEZA'), _format_header)
        worksheet1.write(4, 2, ustr('Código'), _format_header)
        worksheet1.write(4, 3, ustr('Norma de consumo'), _format_header)
        worksheet1.write(4, 4, ustr('Índice de consumo acum'), _format_header)
        worksheet1.write(4, 5, ustr('Consumo plan acum'), _format_header)
        worksheet1.write(4, 6, ustr('Consumo real acum'), _format_header)
        worksheet1.write(4, 7, ustr('Dif (plan - real)'), _format_header)
        z = 5

        listacvl_a, listatcig, listatr, listacnl  = [],[],[],[]

        groups = []
        for item in conf.report_two_product_ids:
            product = item.product_id
            if product.group_number in groups:
                continue

            _products = conf.report_two_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            e, f = float(product.get_consumption_norm(item.uom_id.id)), 0.0
            # f = float(product.total * product.conversion_factor)
            for _p in _products:
                f += float(_p.product_id.total * product.conversion_factor)
            g = float(f / e) if e != 0 else 0.0

            ext = self.env['atm.storeroom_product'].search(
                [('group_product', '=', str(item.product_id.group_number).split('S')[1])], order='date desc', limit=1)

            cont, long, prod_cvl_a, cons_acum = 0, 0, 0, 0
            if item.product_id.destiny_id.code == 'TVL':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['CVL','A']:
                        cont += a.quantity
                        long += 1
                        if date == fecha_last_day:
                            prod_cvl_a += a.quantity
            elif item.product_id.destiny_id.code == 'TCIG':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['CVL','A','CNL']:
                        cont += a.quantity
                        long += 1
                        if date == fecha_last_day:
                            prod_cvl_a += a.quantity
            elif item.product_id.destiny_id.code == 'TR':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['TR']:
                        cont += a.quantity
                        long += 1
                        if date == fecha_last_day:
                            prod_cvl_a += a.quantity
            elif item.product_id.destiny_id.code == 'CNL':
                date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['CNL']:
                        cont += a.quantity
                        long += 1
                        if date == fecha_last_day:
                            prod_cvl_a += a.quantity

            valor = cont / long if long != 0 else 0.0

            entradas = self.env['versat_integration.product_movement'].search(
                [('product_id', '=', item.product_id.id), ('date', '=', fecha_last_day), ('type', '=', 'in')],
                order='date desc', limit=1)
            salidas = self.env['warehouse.product_order'].search(
                [('product_id', '=', item.product_id.id), ('warehouse_request_id.date', '=', fecha_last_day)],
                )

            for p in item.product_id.out_request_ids:
                if p.request_date.split('-')[0] == self.year:
                    cons_acum += p.quantity

            no = product.group_number
            name = product.group_name
            norm = e
            uom = item.uom_id.name
            ext_almacen = f
            ext_panol = ext.quantity_last_day
            ext_total = ext_panol + ext_almacen
            ext_total_act = ext_almacen + ext.quantity
            cob_mcg = ext_total * norm
            cob_dias = ustr(round(cob_mcg / valor, 0) if valor != 0 else 0.0)
            cons_day = ((ext_total - ext_total_act) + entradas.quantity) - salidas.quantity
            ind_cons_day = round(cons_day /prod_cvl_a , 2) if prod_cvl_a != 0 else 0.0
            ind_cons_acum = round(cons_acum / cont, 2) if cont != 0 else 0.0
            num = round(cont / norm, 2) if norm != 0 else 0.0
            worksheet1.write(z, 0, ustr(no), _format_center)
            worksheet1.write(z, 1, ustr(name), style_justified_normal)
            worksheet1.write(z, 2, ustr(item.product_id.code), _format_center)
            worksheet1.write(z, 3, ustr(norm), _format_center)
            worksheet1.write(z, 4, ustr(ind_cons_acum), _format_center)
            worksheet1.write(z, 5, ustr(num), _format_center)
            worksheet1.write(z, 6, ustr(cons_acum), _format_center)
            worksheet1.write(z, 7, ustr(num-cons_acum), _format_center)
            z += 1

            if item.product_id.destiny_id.code == 'TVL':
                dict_cvl_a = {'no': no, 'name': name,'norm': norm ,'uom': uom, 'ext_almacen': ext_almacen, 'ext_panol': ext_panol, 'ext_total': ext_total, 'cob_mcg': cob_mcg, 'cob_dias': cob_dias, 'cons_day':  cons_day, 'ind_cons_day': ind_cons_day, 'cons_acum': cons_acum, 'ind_cons_acum': ind_cons_acum}
                listacvl_a.append(dict_cvl_a)

            if item.product_id.destiny_id.code == 'TCIG':
                dic_tcig = {'no': no, 'name': name,'norm': norm ,'uom': uom, 'ext_almacen': ext_almacen, 'ext_panol': ext_panol, 'ext_total': ext_total, 'cob_mcg': cob_mcg, 'cob_dias': cob_dias, 'cons_day':  cons_day, 'ind_cons_day': ind_cons_day, 'cons_acum': cons_acum, 'ind_cons_acum': ind_cons_acum}
                listatcig.append(dic_tcig)

            if item.product_id.destiny_id.code == 'TR':
                dic_tr = {'no': no, 'name': name,'norm': norm ,'uom': uom, 'ext_almacen': ext_almacen, 'ext_panol': ext_panol, 'ext_total': ext_total, 'cob_mcg': cob_mcg, 'cob_dias': cob_dias, 'cons_day':  cons_day, 'ind_cons_day': ind_cons_day, 'cons_acum': cons_acum, 'ind_cons_acum': ind_cons_acum}
                listatr.append(dic_tr)
            if item.product_id.destiny_id.code == 'CNL':
                dic_cnl = {'no': no, 'name': name,'norm': norm ,'uom': uom, 'ext_almacen': ext_almacen, 'ext_panol': ext_panol, 'ext_total': ext_total, 'cob_mcg': cob_mcg, 'cob_dias': cob_dias, 'cons_day':  cons_day, 'ind_cons_day': ind_cons_day, 'cons_acum': cons_acum, 'ind_cons_acum': ind_cons_acum}
                listacnl.append(dic_cnl)
            groups.append(product.group_number)
        while (destiny < 4):

            worksheet.write_merge(x, y, 0, 0, ustr('No.'), _format)
            if destiny == 0:
                denominacion = ustr('DENOMINACIÓN DE LA PIEZA (Producción de cigarrillos vieja línea)')
                norma = ustr('Norma de consumo MM cig/U')
                cobert = ustr('Millones cigarrillos')
            elif destiny == 1:
                denominacion = ustr('DENOMINACIÓN DE LA PIEZA (Primario)')
                norma = ustr('Norma de consumo ton hebra/U')
                cobert = ustr('Ton hebra')
            elif destiny == 2:
                denominacion = ustr('DENOMINACIÓN DE LA PIEZA (PTR)')
                norma = ustr('Norma de consumo ton tab reconst/U')
                cobert = ustr('Ton tab reconst')
            elif destiny == 3:
                denominacion = ustr('DENOMINACIÓN DE LA PIEZA (Producción de cigarrillos nueva línea)')
                norma = ustr('Norma de consumo MM cig/U')
                cobert = ustr('Millones cigarrillos')

            worksheet.write_merge(x, y, 1, 1, ustr(denominacion), _format_header)
            worksheet.write_merge(x, y, 2, 2, ustr(norma), _format_header)
            worksheet.write_merge(x, y, 3, 3, ustr('U/M'), _format_header)
            worksheet.write_merge(x, y, 4, 4, ustr('Existencia almacén'), _format_header)
            worksheet.write_merge(x, y, 5, 5, ustr('Existencia pañol'), _format_header)
            worksheet.write_merge(x, y, 6, 6, ustr('Existencia total'), _format_header)
            worksheet.write_merge(x, x, 7, 8, ustr('Cobertura'), _format_header)
            worksheet.write_merge(y, y, 7, 7, ustr(cobert), _format_header)
            worksheet.write_merge(y, y, 8, 8, ustr('Días'), _format_header)
            worksheet.write_merge(x, y, 9, 9, ustr('Consumo día'), _format_header)
            worksheet.write_merge(x, y, 10, 10, ustr('Índice de consumo día'), _format_header)
            worksheet.write_merge(x, y, 11, 11, ustr('Consumo acum'), _format_header)
            worksheet.write_merge(x, y, 12, 12, ustr('Índice de consumo acum'), _format_header)
            x += 2

            if destiny == 0:
                for i in listacvl_a:
                    worksheet.write(x, 0, ustr(i['no']), _format_center)
                    worksheet.write(x, 1, ustr(i['name']), style_justified_normal)
                    worksheet.write(x, 2, ustr(i['norm']), _format_center)
                    worksheet.write(x, 3, ustr(i['uom']), _format_center)
                    worksheet.write(x, 4, ustr(i['ext_almacen']), _format_center)
                    worksheet.write(x, 5, ustr(i['ext_panol']), _format_center)
                    worksheet.write(x, 6, ustr(i['ext_total']), _format_center)
                    worksheet.write(x, 7, ustr(i['cob_mcg']), _format_center)
                    worksheet.write(x, 8, ustr(i['cob_dias']), _format_center)
                    worksheet.write(x, 9, ustr(i['cons_day']), _format_center)
                    worksheet.write(x, 10, ustr(i['ind_cons_day']), _format_center)
                    worksheet.write(x, 11, ustr(i['cons_acum']), _format_center)
                    worksheet.write(x, 12, ustr(i['ind_cons_acum']), _format_center)
                    x += 1
            if destiny == 1:
                for i in listatcig:
                    worksheet.write(x, 0, ustr(i['no']), _format_center)
                    worksheet.write(x, 1, ustr(i['name']), style_justified_normal)
                    worksheet.write(x, 2, ustr(i['norm']), _format_center)
                    worksheet.write(x, 3, ustr(i['uom']), _format_center)
                    worksheet.write(x, 4, ustr(i['ext_almacen']), _format_center)
                    worksheet.write(x, 5, ustr(i['ext_panol']), _format_center)
                    worksheet.write(x, 6, ustr(i['ext_total']), _format_center)
                    worksheet.write(x, 7, ustr(i['cob_mcg']), _format_center)
                    worksheet.write(x, 8, ustr(i['cob_dias']), _format_center)
                    worksheet.write(x, 9, ustr(i['cons_day']), _format_center)
                    worksheet.write(x, 10, ustr(i['ind_cons_day']), _format_center)
                    worksheet.write(x, 11, ustr(i['cons_acum']), _format_center)
                    worksheet.write(x, 12, ustr(i['ind_cons_acum']), _format_center)
                    x += 1
            if destiny == 2:
                for i in listatr:
                    worksheet.write(x, 0, ustr(i['no']), _format_center)
                    worksheet.write(x, 1, ustr(i['name']), style_justified_normal)
                    worksheet.write(x, 2, ustr(i['norm']), _format_center)
                    worksheet.write(x, 3, ustr(i['uom']), _format_center)
                    worksheet.write(x, 4, ustr(i['ext_almacen']), _format_center)
                    worksheet.write(x, 5, ustr(i['ext_panol']), _format_center)
                    worksheet.write(x, 6, ustr(i['ext_total']), _format_center)
                    worksheet.write(x, 7, ustr(i['cob_mcg']), _format_center)
                    worksheet.write(x, 8, ustr(i['cob_dias']), _format_center)
                    worksheet.write(x, 9, ustr(i['cons_day']), _format_center)
                    worksheet.write(x, 10, ustr(i['ind_cons_day']), _format_center)
                    worksheet.write(x, 11, ustr(i['cons_acum']), _format_center)
                    worksheet.write(x, 12, ustr(i['ind_cons_acum']), _format_center)
                    x += 1
            if destiny == 3:
                for i in listacnl:
                    worksheet.write(x, 0, ustr(i['no']), _format_center)
                    worksheet.write(x, 1, ustr(i['name']), style_justified_normal)
                    worksheet.write(x, 2, ustr(i['norm']), _format_center)
                    worksheet.write(x, 3, ustr(i['uom']), _format_center)
                    worksheet.write(x, 4, ustr(i['ext_almacen']), _format_center)
                    worksheet.write(x, 5, ustr(i['ext_panol']), _format_center)
                    worksheet.write(x, 6, ustr(i['ext_total']), _format_center)
                    worksheet.write(x, 7, ustr(i['cob_mcg']), _format_center)
                    worksheet.write(x, 8, ustr(i['cob_dias']), _format_center)
                    worksheet.write(x, 9, ustr(i['cons_day']), _format_center)
                    worksheet.write(x, 10, ustr(i['ind_cons_day']), _format_center)
                    worksheet.write(x, 11, ustr(i['cons_acum']), _format_center)
                    worksheet.write(x, 12, ustr(i['ind_cons_acum']), _format_center)
                    x += 1

            y = x + 1
            destiny += 1
        # Section: Other important piezas...
        x += 1
        _format = xlwt.easyxf("font: bold on, colour_index 0x7CCC; align: vert center;")
        worksheet.write(x, 0, 'Otras piezas importantes controladas'.upper(), _format)
        worksheet.gridline_colour_index = 0x40 + 10

        other_piezas = conf.report_two_other_product_ids
        _format = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center;")
        x += 1

        if len(other_piezas):
            worksheet.write(x, 0, 'No.', _format_header)
            worksheet.write(x, 1, ustr('DENOMINACIÓN DE LA PIEZA'), _format_header)
            worksheet.write(x, 2, 'Norma de consumo U/mes', _format_header)
            worksheet.write(x, 3, 'U/M', _format_header)
            worksheet.write(x, 4, ustr('Existencia almacén'), _format_header)
            worksheet.write(x, 5, 'Cobertura(Meses)', _format_header)
            x += 1
            iden = 1
            for rec in other_piezas:
                worksheet.write(x, 0, ustr('OP' + str(iden)), _format_center)
                worksheet.write(x, 1, ustr(rec.product_id.name), style_justified_normal)
                worksheet.write(x, 2, ustr(float(rec.product_id.get_consumption_norm(rec.uom_id.id))), _format_center)
                worksheet.write(x, 3, ustr(item.uom_id.name), _format_center)
                worksheet.write(x, 4, ustr(rec.product_id.total), _format_center)
                worksheet.write(x, 5, ustr(rec.product_id.total / float(rec.product_id.get_consumption_norm(rec.uom_id.id))  if float(rec.product_id.get_consumption_norm(rec.uom_id.id)) != 0 else 0.0), _format_center)
                x += 1
                iden += 1

        worksheet.col(0).width = 0x0d00 - 1500
        worksheet.col(3).width = 0x0d00 - 1500
        worksheet.col(1).width = 0x0d00 + 5000
        worksheet1.col(1).width = 0x0d00 + 5000

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_three(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Parte')
        fecha_last_day = datetime.datetime.now().date() - datetime.timedelta(days=1)
        conf = self.env['atm.report_configuration'].search([], limit=1)

        _format = xlwt.easyxf("font: height 0x00B4; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 0, 11,
                              ustr('PARTE DE COMPRAS, VENTAS Y CONSUMO DE MATERIALES SELECCIONADOS'), _format)
        worksheet.write_merge(1, 1, 0, 11, ustr('FECHA: '+ str(fields.Date.today())), _format)

        _format = xlwt.easyxf(
            "font: height 0x00B4; borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")

        worksheet.write(2, 0, ustr('Materiales'), _format_header)
        worksheet.write(2, 1, ustr('U/M'), _format_header)
        worksheet.write(2, 2, ustr('Compras'), _format_header)
        worksheet.write(2, 3, ustr('Existencia final'), _format_header)
        worksheet.write(2, 4, ustr('Importe de las compras en CUC'), _format_header)
        worksheet.write(2, 5, ustr('Importe de las compras en MN'), _format_header)
        worksheet.write(2, 6, ustr('Importe de las Ventas en CUC'), _format_header)
        worksheet.write(2, 7, ustr('Importe de las Ventas en MN'), _format_header)
        worksheet.write(2, 8, ustr('Plan de consumo'), _format_header)
        worksheet.write(2, 9, ustr('Real consumido'), _format_header)
        worksheet.write(2, 10, ustr('Pérdidas, mermas o deterioro'), _format_header)
        worksheet.write(2, 11, ustr('Ventas'), _format_header)
        x = 3

        groups = []
        comp_a, comp_b, exisf_a, exisf_b, icompcuc_a, icompcuc_b, icompmn_a, icompmn_b, ivencuc_a, ivencuc_b, ivenmn_a, ivenmn_b, pcons_a, pcons_b, rcons_a, rcons_b, salidas_a, salidas_b = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
        for item in conf.report_three_product_ids:
            product = item.product_id
            if product.group_number in groups:
                continue

            _products = conf.report_three_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            e, f = float(product.get_consumption_norm(item.uom_id.id)), 0.0
            # f = float(product.total * product.conversion_factor)
            entradas, salidas = 0.0, 0.0
            for _p in _products:
                f += float(_p.product_id.total * item.conversion_factor)
                for e in self.env['versat_integration.product_movement'].search([('product_id', '=', _p.product_id.id), ('date', '=', fecha_last_day), ('type', '=', 'in')]):
                    entradas += e.quantity
                for s in self.env['warehouse.product_order'].search([('product_id', '=', _p.product_id.id), ('warehouse_request_id.date', '=', fecha_last_day)]):
                    salidas += s.quantity

            produccion = 0
            if item.product_id.destiny_id.code == 'TVL':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['CVL','A']:
                        if date == fecha_last_day:
                            produccion += a.quantity
            elif item.product_id.destiny_id.code == 'TCIG':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['CVL','A','CNL']:
                        if date == fecha_last_day:
                            produccion += a.quantity
            elif item.product_id.destiny_id.code == 'TR':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    if a.destiny_id.code in ['TR']:
                        if date == fecha_last_day:
                            produccion += a.quantity
            elif item.product_id.destiny_id.code == 'CNL':
                date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['CNL']:
                        if date == fecha_last_day:
                            produccion += a.quantity
            elif item.product_id.destiny_id.code == 'A':
                date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['A']:
                        if date == fecha_last_day:
                            produccion += a.quantity

            if item.product_id.group_number in ['MF10','MF11']:
               name_a = 'Polipropileno'
               um_a = item.uom_id.name
               comp_a += entradas * item.conversion_factor
               exisf_a += f
               icompcuc_a += round(entradas * item.product_id.price_extra, 2)
               icompmn_a += round(entradas * item.product_id.price, 2)
               ivencuc_a += round(salidas * item.product_id.price_extra, 2)
               ivenmn_a += round(salidas * item.product_id.price, 2)
               pcons_a += round(produccion * float(item.product_id.get_consumption_norm(item.uom_id.id)), 2)
               rcons_a += ((f-entradas)+salidas)
               salidas_a += salidas

            elif item.product_id.group_number in ['MF13','MF14','MF15']:
                name_b = 'Sellos para cigarros'
                um_b =item.uom_id.name
                comp_b += entradas * item.conversion_factor
                exisf_b += f
                icompcuc_b += round(entradas * item.product_id.price_extra, 2)
                icompmn_b += round(entradas * item.product_id.price, 2)
                ivencuc_b += round(salidas * item.product_id.price_extra, 2)
                ivenmn_b += round(salidas * item.product_id.price, 2)
                pcons_b += round(produccion * float(item.product_id.get_consumption_norm(item.uom_id.id)), 2)
                rcons_b += ((f-entradas)+salidas)
                salidas_b += salidas
            else:
                worksheet.write(x, 0, ustr(item.product_id.group_name), style_justified_normal)
                worksheet.write(x, 1, ustr(item.uom_id.name), _format_center)
                worksheet.write(x, 2, ustr(entradas * item.conversion_factor), _format_center)
                worksheet.write(x, 3, ustr(f), _format_center)
                worksheet.write(x, 4, ustr(round(entradas * item.product_id.price_extra, 2)), _format_center)
                worksheet.write(x, 5, ustr(round(entradas * item.product_id.price, 2)), _format_center)
                worksheet.write(x, 6, ustr(round(salidas * item.product_id.price_extra, 2)), _format_center)
                worksheet.write(x, 7, ustr(round(salidas * item.product_id.price, 2)), _format_center)
                worksheet.write(x, 8, ustr(round(produccion * float(item.product_id.get_consumption_norm(item.uom_id.id)), 2)), _format_center)
                worksheet.write(x, 9, ustr(((f-entradas)+salidas)), _format_center)
                worksheet.write(x, 10, ustr(" "), _format_center)
                worksheet.write(x, 11, ustr(salidas), _format_center)
                x += 1

            groups.append(product.group_number)

        worksheet.write(x, 0, ustr(name_a), style_justified_normal)
        worksheet.write(x, 1, ustr(um_a), _format_center)
        worksheet.write(x, 2, ustr(comp_a), _format_center)
        worksheet.write(x, 3, ustr(exisf_a), _format_center)
        worksheet.write(x, 4, ustr(icompcuc_a), _format_center)
        worksheet.write(x, 5, ustr(icompmn_a), _format_center)
        worksheet.write(x, 6, ustr(ivencuc_a), _format_center)
        worksheet.write(x, 7, ustr(ivenmn_a), _format_center)
        worksheet.write(x, 8, ustr(pcons_a), _format_center)
        worksheet.write(x, 9, ustr(rcons_a), _format_center)
        worksheet.write(x, 10, ustr(" "), _format_center)
        worksheet.write(x, 11, ustr(salidas_a), _format_center)
        x += 1

        worksheet.write(x, 0, ustr(name_b), style_justified_normal)
        worksheet.write(x, 1, ustr(um_b), _format_center)
        worksheet.write(x, 2, ustr(comp_b), _format_center)
        worksheet.write(x, 3, ustr(exisf_b), _format_center)
        worksheet.write(x, 4, ustr(icompcuc_b), _format_center)
        worksheet.write(x, 5, ustr(icompmn_b), _format_center)
        worksheet.write(x, 6, ustr(ivencuc_b), _format_center)
        worksheet.write(x, 7, ustr(ivenmn_b), _format_center)
        worksheet.write(x, 8, ustr(pcons_b), _format_center)
        worksheet.write(x, 9, ustr(rcons_b), _format_center)
        worksheet.write(x, 10, ustr(" "), _format_center)
        worksheet.write(x, 11, ustr(salidas_b), _format_center)
        x += 1


        worksheet.col(0).width = 0x0d00 + 5000

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_four(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Cumplimiento Fisico')
        fecha_last_day = datetime.datetime.now().date() - datetime.timedelta(days=1)
        _format = xlwt.easyxf("font: height 0x00B4; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 0, 11,
                              ustr('CUMPLIMIENTO DEL PLAN FÍSICO DE LOS MATERIALES FUNDAMENTALES EN EL ' + str(self.year)), _format)
        worksheet.write_merge(1, 1, 0, 11,
                              ustr('PERÍODO  DESDE: ENERO         HASTA: ' + str(self.month) + '    DEL: '  + str(self.year)), _format)

        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_critic = xlwt.easyxf('pattern: pattern solid, fore_colour red; borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center')

        worksheet.write_merge(3, 4, 0, 0, ustr('No'), _format_header)
        worksheet.write_merge(3, 4, 1, 1, ustr('MATERIALES'), _format_header)
        worksheet.write_merge(3, 4, 2, 2, ustr('U/M'), _format_header)
        worksheet.write_merge(3, 4, 3, 3, ustr('PLAN'), _format_header)
        worksheet.write_merge(3, 3, 4, 7, ustr('MES'), _format_header)
        worksheet.write_merge(4, 4, 4, 4, ustr('PLAN'), _format_header)
        worksheet.write_merge(4, 4, 5, 5, ustr('REAL'), _format_header)
        worksheet.write_merge(4, 4, 6, 6, ustr('%'), _format_header)
        worksheet.write_merge(4, 4, 7, 7, ustr('DIFERENCIA'), _format_header)
        worksheet.write_merge(3, 3, 8, 11, ustr('ACUMULADO'), _format_header)
        worksheet.write_merge(4, 4, 8, 8, ustr('PLAN'), _format_header)
        worksheet.write_merge(4, 4, 9, 9, ustr('REAL'), _format_header)
        worksheet.write_merge(4, 4, 10, 10, ustr('%'), _format_header)
        worksheet.write_merge(4, 4, 11, 11, ustr('DIFERENCIA'), _format_header)

        conf = self.env['atm.report_configuration'].search([], limit=1)
        x = 5

        groups = []
        for item in conf.report_four_product_ids:
            product = item.product_id
            if product.group_number in groups:
                continue

            _products = conf.report_four_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            f, plan =  0.0, 0.0
            for _p in _products:
                f += float(_p.product_id.total * product.conversion_factor)

            for des in self.env['atm.production_plan'].search([('year', '=', self.year)]):
                for p in self.env['atm.plan_record'].search([('destiny_id','=',product.destiny_id.id),('plan_id','=', des.id)]):
                    plan = p.plan01+p.plan02+p.plan03+p.plan04+p.plan05+p.plan06+p.plan07+p.plan08+p.plan09+p.plan10+p.plan11+p.plan12
                    dic = {'01':p.plan01, '02':p.plan02, '03':p.plan03, '04':p.plan04, '05':p.plan05, '06':p.plan06, '07':p.plan07, '08':p.plan08, '09':p.plan09, '10':p.plan10, '11':p.plan11, '12':p.plan12}

            cont, cons_acum = 0, 0
            if item.product_id.destiny_id.code == 'TVL':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['CVL','A']:
                        if a.date.split('-')[1] == number_months_dict[self.month]:
                            cont += a.quantity
                        if a.date.split('-')[1] <= number_months_dict[self.month]:
                            cons_acum += a.quantity
            elif item.product_id.destiny_id.code == 'TCIG':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['CVL','A','CNL']:
                        if a.date.split('-')[1] == number_months_dict[self.month]:
                            cont += a.quantity
                        if a.date.split('-')[1] <= number_months_dict[self.month]:
                            cons_acum += a.quantity
            elif item.product_id.destiny_id.code == 'TR':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['TR']:
                        if a.date.split('-')[1] == number_months_dict[self.month]:
                            cont += a.quantity
                        if a.date.split('-')[1] <= number_months_dict[self.month]:
                            cons_acum += a.quantity
            elif item.product_id.destiny_id.code == 'CNL':
                for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                    if a.destiny_id.code in ['CNL']:
                        if a.date.split('-')[1] == number_months_dict[self.month]:
                            cont += a.quantity
                        if a.date.split('-')[1] <= number_months_dict[self.month]:
                            cons_acum += a.quantity

            plan_acum = 0.0
            list_final = int(number_months_dict[self.month]) + 1
            for i in xrange(1,list_final):
                if i < 10:
                    v = '0' + str(i)
                else:
                    v = str(i)
                plan_acum += dic[v]
            neg_mes = True if int(dic[number_months_dict[self.month]]) > cont else False
            neg_acum = True if (plan_acum * item.conversion_factor) > (cons_acum * item.conversion_factor) else False

            worksheet.write(x, 0, ustr(item.product_id.group_number), _format_center)
            worksheet.write(x, 1, ustr(item.product_id.group_name), style_justified_normal)
            worksheet.write(x, 2, ustr(item.uom_id.name), _format_center)
            worksheet.write(x, 3, ustr(round(plan * item.conversion_factor,2) ), _format_center)
            worksheet.write(x, 4, ustr(round(dic[number_months_dict[self.month]] * item.conversion_factor,2)), _format_center)
            worksheet.write(x, 5, ustr(round(cont * item.conversion_factor,2)), _format_center)
            worksheet.write(x, 6, ustr(round((cont * item.conversion_factor) * 100 / (dic[number_months_dict[self.month]] * item.conversion_factor) if (dic[number_months_dict[self.month]] * item.conversion_factor) != 0 else 0.0, 1)), _format_center)
            worksheet.write(x, 7, ustr(round((cont * item.conversion_factor)-(dic[number_months_dict[self.month]] * item.conversion_factor),2)), _format_critic if neg_mes else _format_center)
            worksheet.write(x, 8, ustr(round(plan_acum * item.conversion_factor,2)), _format_center)
            worksheet.write(x, 9, ustr(round(cons_acum * item.conversion_factor,2)), _format_center)
            worksheet.write(x, 10, ustr(round((cons_acum * item.conversion_factor) * 100 / (plan_acum * item.conversion_factor) if plan_acum != 0 else 0.0, 1)), _format_center)
            worksheet.write(x, 11, ustr(round((cons_acum * item.conversion_factor)-(plan_acum * item.conversion_factor),2)), _format_critic if neg_acum else _format_center)
            x += 1

            groups.append(product.group_number)

        worksheet.col(0).width = 0x0d00 - 1500
        worksheet.col(1).width = 0x0d00 + 5000
        worksheet.col(2).width = 0x0d00 - 1500
        worksheet.col(6).width = 0x0d00 - 1500
        worksheet.col(7).width = 0x0d00 + 1000
        worksheet.col(10).width = 0x0d00 - 1500
        worksheet.col(11).width = 0x0d00 + 1000

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_five(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Parte')
        fecha_last_day = datetime.datetime.now().date() - datetime.timedelta(days=1)
        _format = xlwt.easyxf("font: height 0x00B4; font: bold on; align: wrap on, horiz center, vert center")
        worksheet.write_merge(0, 0, 0, 9, ustr('MINISTERIO DE LA AGRICULTURA'), _format)
        worksheet.write_merge(1, 1, 0, 9, ustr('EMPRESA DE CIGARROS "LÁZARO PEÑA"'), _format)
        worksheet.write_merge(2, 2, 0, 9, ustr('INFORME DE MATERIALES Y MATERIAS PRIMAS CRÍTICOS'), _format)
        worksheet.write_merge(3, 3, 0, 9, ustr('DEPARTAMENTO DE LOGÍSTICA'), _format)
        worksheet.write_merge(4, 4, 0, 9, fields.Date.today(), _format)
        x = 5
        y = 6
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_critic = xlwt.easyxf('pattern: pattern solid, fore_colour red; borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center')

        conf = self.env['atm.report_configuration'].search([], limit=1)
        general_plan, dict_values = self.env['atm.production_plan'].search([('year', '=', self.year)]), {}
        current_month = datetime.date(int(self.year), int(number_months_dict[self.month]), 10)

        worksheet.write_merge(x, y, 0, 0, ustr('No.'), _format_header)
        worksheet.write_merge(x, y, 1, 1, ustr('PRODUCTO'), _format_header)
        worksheet.write_merge(x, y, 2, 2, ustr('U/M'), _format_header)
        worksheet.write_merge(x, x, 3, 4, ustr('PLAN CONTRATADO'), _format_header)
        worksheet.write_merge(y, y, 3, 3, ustr('Año'), _format_header)
        worksheet.write_merge(y, y, 4, 4, ustr('Hasta la fecha'), _format_header)
        worksheet.write_merge(x, x, 5, 6, ustr('REAL'), _format_header)
        worksheet.write_merge(y, y, 5, 5, ustr('Recibido'), _format_header)
        worksheet.write_merge(y, y, 6, 6, ustr('En existencia'), _format_header)
        worksheet.write_merge(x, y, 7, 7, ustr('%'), _format_header)
        worksheet.write_merge(x, y, 8, 8, ustr('DÍAS DE COBERTURA'), _format_header)
        worksheet.write_merge(x, y, 9, 9, ustr('MILLONES DE COBERTURA'), _format_header)
        x = y+1
        write_table1 = True
        write_table2 = True
        write_table3 = True
        for record in general_plan.record_ids:
            dict_values[record.destiny_id.code] = getattr(record, 'plan%s' % (current_month.strftime('%m'),), 0.0)

        groups = []
        for item in conf.report_one_product_ids:
            product = item.product_id
            if product.group_number in groups:
                continue

            _products = conf.report_one_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            e, f = float(product.get_consumption_norm(item.uom_id.id)), 0.0
            # f = float(product.total * product.conversion_factor)
            for _p in _products:
                f += float(_p.product_id.total * _p.product_id.conversion_factor)
            g = float(f / e) if e != 0 else 0.0

            daily_plan = 0.0
            if product.formula_month_plan:
                daily_plan = eval(product.formula_month_plan, dict_values)

            dp = float(daily_plan) / conf.working_days if conf.working_days != 0.0 else 0.0
            coverage_in_days = (g / dp) if dp > 0 else 0.0
            is_critic = True if (product.origin == 'national' and coverage_in_days < 30 and product.destiny_id.code in [
                'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'national' and g < 30 and product.destiny_id.code in ['A']) or (
                                    product.origin == 'international' and coverage_in_days < 90 and product.destiny_id.code in [
                                        'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'international' and g < 90 and product.destiny_id.code in [
                                        'A']) else False

            if is_critic:
                write_table1 = False
                for des in self.env['atm.production_plan'].search([('year', '=', self.year)]):
                    for p in self.env['atm.plan_record'].search([('destiny_id','=',product.destiny_id.id),('plan_id','=', des.id)]):
                        plan = p.plan01+p.plan02+p.plan03+p.plan04+p.plan05+p.plan06+p.plan07+p.plan08+p.plan09+p.plan10+p.plan11+p.plan12
                        dic = {'01':p.plan01, '02':p.plan02, '03':p.plan03, '04':p.plan04, '05':p.plan05, '06':p.plan06, '07':p.plan07, '08':p.plan08, '09':p.plan09, '10':p.plan10, '11':p.plan11, '12':p.plan12}

                cont, cons_acum = 0, 0
                if item.product_id.destiny_id.code == 'TVL':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        if a.destiny_id.code in ['CVL','A']:
                            if a.date.split('-')[1] == number_months_dict[self.month]:
                                cont += a.quantity
                            if a.date.split('-')[1] <= number_months_dict[self.month]:
                                cons_acum += a.quantity
                elif item.product_id.destiny_id.code == 'TCIG':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        if a.destiny_id.code in ['CVL','A','CNL']:
                            if a.date.split('-')[1] == number_months_dict[self.month]:
                                cont += a.quantity
                            if a.date.split('-')[1] <= number_months_dict[self.month]:
                                cons_acum += a.quantity
                elif item.product_id.destiny_id.code == 'TR':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        if a.destiny_id.code in ['TR']:
                            if a.date.split('-')[1] == number_months_dict[self.month]:
                                cont += a.quantity
                            if a.date.split('-')[1] <= number_months_dict[self.month]:
                                cons_acum += a.quantity
                elif item.product_id.destiny_id.code == 'CNL':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        if a.destiny_id.code in ['CNL']:
                            if a.date.split('-')[1] == number_months_dict[self.month]:
                                cont += a.quantity
                            if a.date.split('-')[1] <= number_months_dict[self.month]:
                                cons_acum += a.quantity

                plan_acum = 0.0
                list_final = int(number_months_dict[self.month]) + 1
                for i in xrange(1,list_final):
                    if i < 10:
                        v = '0' + str(i)
                    else:
                        v = str(i)
                    plan_acum += dic[v]
                worksheet.write(x, 0, ustr(product.group_number), _format_center)
                worksheet.write(x, 1, ustr(product.group_name), style_justified_normal)
                worksheet.write(x, 2, ustr(item.uom_id.name), _format_center)
                worksheet.write(x, 3, ustr(plan * item.conversion_factor), _format_center)
                worksheet.write(x, 4, ustr(plan_acum * item.conversion_factor), _format_center)
                worksheet.write(x, 5, ustr(cons_acum * item.conversion_factor), _format_center)
                worksheet.write(x, 6, ustr(round(f, 1)), _format_center)
                worksheet.write(x, 7, ustr(round((((cons_acum * item.conversion_factor)*100)/(plan_acum * item.conversion_factor) if (plan_acum * item.conversion_factor) !=0 else 0.0),1)), _format_center)
                worksheet.write(x, 8, ustr(round(coverage_in_days, 1)), _format_center)
                worksheet.write(x, 9, ustr(round(g, 1)), _format_center)
                x += 1
            groups.append(product.group_number)
        if write_table1:
            worksheet.write_merge(x, x, 0, 9, ustr('No hay Materiales Fundamentales Criticos'), _format_header)
            x += 1
        x += 1
        worksheet.write(x, 0, ustr('No.'), _format_header)
        worksheet.write(x, 1, ustr('DENOMINACIÓN DE LA PIEZA'), _format_header)
        worksheet.write(x, 2, ustr('Norma de Consumo'), _format_header)
        worksheet.write(x, 3, ustr('U/M'), _format_header)
        worksheet.write(x, 4, ustr('Existencia almacén'), _format_header)
        worksheet.write(x, 5, ustr('Existencia pañol'), _format_header)
        worksheet.write(x, 6, ustr('Existencia total'), _format_header)
        worksheet.write(x, 7, ustr('Cobertura millones de cigarrillos'), _format_header)
        worksheet.write(x, 8, ustr('Cobertura días'), _format_header)
        x += 1

        for item in conf.report_two_product_ids:
            product = item.product_id
            _products = conf.report_two_product_ids.filtered(
                lambda x: x.product_id.group_number == product.group_number)
            e, f = float(product.get_consumption_norm(item.uom_id.id)), 0.0
            # f = float(product.total * product.conversion_factor)
            for _p in _products:
                f += float(_p.product_id.total * _p.product_id.conversion_factor)
            g = float(f / e) if e != 0 else 0.0
            daily_plan = 0.0
            if product.formula_month_plan:
                daily_plan = eval(product.formula_month_plan, dict_values)

            dp = float(daily_plan) / conf.working_days if conf.working_days != 0.0 else 0.0
            coverage_in_days = (g / dp) if dp > 0 else 0.0
            is_critic = True if (product.origin == 'national' and coverage_in_days < 30 and product.destiny_id.code in [
                'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'national' and g < 30 and product.destiny_id.code in ['A']) or (
                                    product.origin == 'international' and coverage_in_days < 90 and product.destiny_id.code in [
                                        'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                    product.origin == 'international' and g < 90 and product.destiny_id.code in [
                                        'A']) else False

            if is_critic:
                write_table2 = False

                ext = self.env['atm.storeroom_product'].search(
                [('group_product', '=', str(item.product_id.group_number).split('S')[1])], order='date desc', limit=1)

                cont, long, prod_cvl_a, cons_acum = 0, 0, 0, 0
                if item.product_id.destiny_id.code == 'TVL':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                        if a.destiny_id.code in ['CVL','A']:
                            cont += a.quantity
                            long += 1
                            if date == fecha_last_day:
                                prod_cvl_a += a.quantity
                elif item.product_id.destiny_id.code == 'TCIG':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                        if a.destiny_id.code in ['CVL','A','CNL']:
                            cont += a.quantity
                            long += 1
                            if date == fecha_last_day:
                                prod_cvl_a += a.quantity
                elif item.product_id.destiny_id.code == 'TR':
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                        if a.destiny_id.code in ['TR']:
                            cont += a.quantity
                            long += 1
                            if date == fecha_last_day:
                                prod_cvl_a += a.quantity
                elif item.product_id.destiny_id.code == 'CNL':
                    date = datetime.date(int(a.date.split("-")[0]),int(a.date.split("-")[1]),int(a.date.split("-")[2]))
                    for a in self.env['atm.daily_production'].search([('year', '=', self._default_get_year())]):
                        if a.destiny_id.code in ['CNL']:
                            cont += a.quantity
                            long += 1
                            if date == fecha_last_day:
                                prod_cvl_a += a.quantity

                valor = cont / long if long != 0 else 0.0

                entradas = self.env['versat_integration.product_movement'].search(
                    [('product_id', '=', item.product_id.id), ('date', '=', fecha_last_day), ('type', '=', 'in')],
                    order='date desc', limit=1)
                salidas = self.env['warehouse.product_order'].search(
                    [('product_id', '=', item.product_id.id), ('warehouse_request_id.date', '=', fecha_last_day)],
                    )

                worksheet.write(x, 0, ustr(product.group_number), _format_center)
                worksheet.write(x, 1, ustr(product.group_name), _format_center)
                worksheet.write(x, 2, ustr(float(item.product_id.get_consumption_norm(item.uom_id.id))), _format_center)
                worksheet.write(x, 3, ustr(item.uom_id.name), _format_center)
                worksheet.write(x, 4, ustr(f), _format_center)
                worksheet.write(x, 5, ustr(ext.quantity_last_day), _format_center)
                worksheet.write(x, 6, ustr(ext.quantity_last_day + f), _format_center)
                cob_mcg = (ext.quantity_last_day + f) * float(item.product_id.get_consumption_norm(item.uom_id.id))
                worksheet.write(x, 7, ustr(cob_mcg), _format_center)
                cob_dias = ustr(round(cob_mcg / valor, 0) if valor != 0 else 0.0)
                worksheet.write(x, 8, ustr(cob_dias), _format_center)
                x += 1
        if write_table2:
            worksheet.write_merge(x, x, 0, 8, ustr('No hay Gastables Criticos'), _format_header)
            x += 1

        other_piezas = conf.report_two_other_product_ids
        x += 1
        if len(other_piezas):
            worksheet.write(x, 0, 'No.', _format_header)
            worksheet.write(x, 1, ustr('DENOMINACIÓN DE LA PIEZA'), _format_header)
            worksheet.write(x, 2, 'Norma de consumo U/mes', _format_header)
            worksheet.write(x, 3, 'U/M', _format_header)
            worksheet.write(x, 4, ustr('Existencia almacén'), _format_header)
            worksheet.write(x, 5, 'Cobertura(Meses)', _format_header)
            x += 1
            iden = 1
            for rec in other_piezas:
                product = rec.product_id

                e = float(product.get_consumption_norm(item.uom_id.id))
                # f = float(product.total * product.conversion_factor)
                f = rec.product_id.total
                g = float(f / e) if e != 0 else 0.0
                daily_plan = 0.0
                if product.formula_month_plan:
                    daily_plan = eval(product.formula_month_plan, dict_values)

                dp = float(daily_plan) / conf.working_days if conf.working_days != 0.0 else 0.0
                coverage_in_days = (g / dp) if dp > 0 else 0.0
                is_critic = True if (product.origin == 'national' and coverage_in_days < 30 and product.destiny_id.code in [
                    'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                        product.origin == 'national' and g < 30 and product.destiny_id.code in ['A']) or (
                                        product.origin == 'international' and coverage_in_days < 90 and product.destiny_id.code in [
                                            'TR', 'TC', 'CNL', 'CVL', 'TVL']) or (
                                        product.origin == 'international' and g < 90 and product.destiny_id.code in [
                                            'A']) else False

                if is_critic:
                    write_table3 = False
                    worksheet.write(x, 0, ustr('OP' + str(iden)), _format_center)
                    worksheet.write(x, 1, ustr(rec.product_id.name), style_justified_normal)
                    worksheet.write(x, 2, ustr(float(rec.product_id.get_consumption_norm(rec.uom_id.id))), _format_center)
                    worksheet.write(x, 3, ustr(item.uom_id.name), _format_center)
                    worksheet.write(x, 4, ustr(rec.product_id.total), _format_center)
                    worksheet.write(x, 5, ustr(rec.product_id.total / float(rec.product_id.get_consumption_norm(rec.uom_id.id))  if float(rec.product_id.get_consumption_norm(rec.uom_id.id)) != 0 else 0.0), _format_center)
                    x += 1
                    iden += 1
            if write_table3:
                worksheet.write_merge(x, x, 0, 5, ustr('No hay Otras Piezas Criticos'), _format_header)
                x += 1
        worksheet.col(0).width = 0x0d00 - 1500
        worksheet.col(1).width = 0x0d00 + 5000
        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_six(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Page1')

        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")
        worksheet.write(0, 0, ustr('Número de factura'), _format_header)
        worksheet.write(0, 1, ustr('Almacén'), _format_header)
        worksheet.write(0, 2, ustr('Descripción del producto'), _format_header)
        worksheet.write(0, 3, ustr('U/M'), _format_header)
        worksheet.write(0, 4, ustr('Cant'), _format_header)
        worksheet.write(0, 5, ustr('Contenedor o casilla'), _format_header)
        worksheet.write(0, 6, ustr('Matrícula'), _format_header)
        worksheet.write(0, 7, ustr('Transportista'), _format_header)
        worksheet.write(0, 8, ustr('Procedencia'), _format_header)
        worksheet.write(0, 9, ustr('Fecha y hora'), _format_header)
        x = 1

        fecha_last_day = datetime.date(int(fields.Date.today().split('-')[0]), int(fields.Date.today().split('-')[1]), int(fields.Date.today().split('-')[2]))
        blind_recep = self.env['atm.blind_reception'].search(['|',('warehouse_id.code', '=', '03'),('warehouse_id.code', '=', '04')])
        for br in blind_recep:
            fecha = datetime.date(int(br.creation_date.split(' ')[0].split('-')[0]), int(br.creation_date.split(' ')[0].split('-')[1]), int(br.creation_date.split(' ')[0].split('-')[2]))
            if fecha == fecha_last_day:
                for p in br.product_ids:
                    worksheet.write(x, 0, ustr(br.invoice_number), _format_center)
                    worksheet.write(x, 1, ustr(br.warehouse_id.code), _format_center)
                    worksheet.write(x, 2, ustr(p.product_description), _format_center)
                    worksheet.write(x, 3, ustr(p.uom_id.name), _format_center)
                    worksheet.write(x, 4, ustr(p.quantity), _format_center)
                    worksheet.write(x, 5, ustr(br.container_or_box or ''), _format_center)
                    worksheet.write(x, 6, ustr(br.car_plate), _format_center)
                    worksheet.write(x, 7, ustr(br.driver_id.name), _format_center)
                    worksheet.write(x, 8, ustr(br.supplier_id.name), _format_center)
                    f = datetime.datetime(int(br.creation_date.split(' ')[0].split('-')[0]), int(br.creation_date.split(' ')[0].split('-')[1]), int(br.creation_date.split(' ')[0].split('-')[2]), int(br.creation_date.split(' ')[1].split(':')[0]),int(br.creation_date.split(' ')[1].split(':')[1]),int(br.creation_date.split(' ')[1].split(':')[2])) - datetime.timedelta(hours=5)
                    worksheet.write(x, 9, ustr(f), _format_center)
                    x += 1

        blind_recep_other = self.env['atm.blind_reception'].search([('warehouse_id.code', '=', '10')])
        conf = self.env['atm.report_configuration'].search([], limit=1)
        products = conf.report_six_product_ids

        for bro in blind_recep_other:
            fecha = datetime.date(int(bro.creation_date.split(' ')[0].split('-')[0]), int(bro.creation_date.split(' ')[0].split('-')[1]), int(bro.creation_date.split(' ')[0].split('-')[2]))
            if fecha == fecha_last_day:
                for p in products:
                    if p.product_description == bro.product_ids.product_description:
                        for pr in bro.product_ids:
                            worksheet.write(x, 0, ustr(bro.invoice_number), _format_center)
                            worksheet.write(x, 1, ustr(bro.warehouse_id.code), _format_center)
                            worksheet.write(x, 2, ustr(pr.product_description), _format_center)
                            worksheet.write(x, 3, ustr(pr.uom_id.name), _format_center)
                            worksheet.write(x, 4, ustr(pr.quantity), _format_center)
                            worksheet.write(x, 5, ustr(bro.container_or_box or ''), _format_center)
                            worksheet.write(x, 6, ustr(bro.car_plate), _format_center)
                            worksheet.write(x, 7, ustr(bro.driver_id.name), _format_center)
                            worksheet.write(x, 8, ustr(bro.supplier_id.name), _format_center)
                            #worksheet.write(x, 9, ustr(bro.creation_date), _format_center)
                            f = datetime.datetime(int(br.creation_date.split(' ')[0].split('-')[0]), int(br.creation_date.split(' ')[0].split('-')[1]), int(br.creation_date.split(' ')[0].split('-')[2]), int(br.creation_date.split(' ')[1].split(':')[0]),int(br.creation_date.split(' ')[1].split(':')[1]),int(br.creation_date.split(' ')[1].split(':')[2])) - datetime.timedelta(hours=5)
                            worksheet.write(x, 9, ustr(f), _format_center)

                            x += 1



        worksheet.col(0).width = 0x0d00 + 1500
        worksheet.col(2).width = 0x0d00 + 5000
        worksheet.col(3).width = 0x0d00 - 1500
        worksheet.col(5).width = 0x0d00 + 1500
        worksheet.col(7).width = 0x0d00 + 2500
        worksheet.col(8).width = 0x0d00 + 1500
        worksheet.col(9).width = 0x0d00 + 1500

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def report_seven(self):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('Salida')

        _format_header = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; font: bold on; align: wrap on, horiz center, vert center")
        _format_center = xlwt.easyxf(
            "borders: right 1, left 1, top 1, bottom 1; align: wrap on, horiz center, vert center")

        worksheet.write(0, 0, ustr('No SOLICITUD'), _format_header)
        worksheet.write(0, 1, ustr('FECHA'), _format_header)
        worksheet.write(0, 2, ustr('ALMACÉN'), _format_header)
        worksheet.write(0, 3, ustr('CÓDIGO'), _format_header)
        worksheet.write(0, 4, ustr('DESCRIPCIÓN'), _format_header)
        worksheet.write(0, 5, ustr('U/M'), _format_header)
        worksheet.write(0, 6, ustr('CANT'), _format_header)
        worksheet.write(0, 7, ustr('ÁREA DE RESPONSABILIDAD'), _format_header)
        worksheet.write(0, 8, ustr('CENTRO DE COSTO'), _format_header)
        worksheet.write(0, 9, ustr('ORDEN TRABAJO'), _format_header)
        worksheet.write(0, 10, ustr('SOLICITADO POR:'), _format_header)
        x = 1

        nw = self.env['warehouse.warehouse_request'].search(['|',('work_order_id.number', 'like', 'P2'),'|',('cost_center_id.code', 'like', '60'),('work_order_id.number', 'like', 'A2'),('date', '=', fields.Date.today())])
        for a in nw:
            for p in a.requested_product_ids:
                worksheet.write(x, 0, ustr(a.code), _format_center)
                worksheet.write(x, 1, ustr(a.date), _format_center)
                worksheet.write(x, 2, ustr(a.warehouse_id.code), _format_center)
                worksheet.write(x, 3, ustr(p.product_id.code), _format_center)
                worksheet.write(x, 4, ustr(p.product_id.name), _format_center)
                worksheet.write(x, 5, ustr(p.product_id.uom_id.name), _format_center)
                worksheet.write(x, 6, ustr(p.quantity), _format_center)
                worksheet.write(x, 7, ustr(a.responsibility_area_id.name), _format_center)
                worksheet.write(x, 8, ustr(a.cost_center_id.name), _format_center)
                worksheet.write(x, 9, ustr(a.work_order_id.number), _format_center)
                worksheet.write(x, 10, ustr(a.applicant_id.name), _format_center)
                x += 1

        worksheet.col(4).width = 0x0d00 + 5000
        worksheet.col(5).width = 0x0d00 - 1500
        worksheet.col(7).width = 0x0d00 + 2000
        worksheet.col(8).width = 0x0d00 + 2000
        worksheet.col(10).width = 0x0d00 + 2000

        output = cStringIO.StringIO()
        workbook.save(output)
        output.seek(0)
        data = output.read()
        output.close()
        return data

    @api.model
    def get_content_type(self):
        return 'application/vnd.ms-excel'
