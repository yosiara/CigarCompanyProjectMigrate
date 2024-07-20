# -*- coding: utf-8 -*-

#from openerp import models, fields, api
from openerp.osv import fields, osv
from openerp import tools
import codecs

import logging
_logger = logging.getLogger(__name__)

class df_locals_import(osv.osv_memory):
    _name = "df_locals.import_wzd"
    _columns = {
                #TODO : import time required to get currect date
                #'fecha_inicio': fields.date('Fecha inicio'),
                }

    def clean_str(self,texto):
        text=tools.ustr(texto)
        #text.replace('¾','ó').replace('Ý','í').replace('ß','á').replace('Ú','é').replace('±','ñ').replace('┴','A')
        return text 

    def get_area(self, conn):
        """ Get area from versat"""
        cursor = conn.cursor()
        cursor.execute("""
        SELECT clave,clavenivel,descripcion  FROM gen_area  Order by clave;
        """)
        res = []
        for row in cursor:
            res.append((row[0],row[1],row[2]))
        return res
    
    
    def do_import_area(self, cr, uid, ids, context=None, conn=None):
        disconnect = False
        if not conn:
            conn_obj = self.pool.get('df_sqlserver.template')
            conn = conn_obj.connect(cr, uid, context=context)
            disconnect = True
        dep_obj = self.pool.get('l10n_cu_locals.local')
        
        for area_full_code,area_code,area_name in self.get_area(conn):
            #Busco por el codigo del departamento
            #el self.clean_str es un parche por los problemas de incompatibilidad en la codificacion
            area_full_code=self.clean_str(area_full_code)
            area_name=self.clean_str(area_name)
            area_ids = dep_obj.search(cr, uid, [('code','=',area_full_code)], context=context)
            #Si no está el departamento se crea
            if not area_ids:
                dep_obj.create(cr, uid, {
                                            'name': area_name,
                                            'code': area_full_code,
                                            }, context=context)
                _logger.info("Area creada: %s en %s",area_full_code,area_name)
            else:
                dep_obj.write(cr, uid,area_ids[0],{'name': area_name,}, context=context)

        if disconnect:
            conn.close()
        
    def run_import_area(self, cr, uid, conn_name, context=None):
        """ 
        SCHEDULE TASK
        CREA IMPORTAR EMPLEADOS PRIODICAMENTE
        """ 
        """INACTIVO LAS CONEXXIONES Y ACTIVO SEGUN LA TAREA"""
        conn_obj = self.pool.get('df_sqlserver.template')
        if conn_obj.change_active_connection( cr, uid, conn_name,context=context):
            _logger.info("lanzada la tarea programada.")     
            self.do_import_area(cr, uid, self.search(cr, uid, [], context=context))
            return True
        else:
            _logger.info("No se lanzó la tarea programada.")
    


    
    
    