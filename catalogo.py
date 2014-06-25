# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import date
from openerp import netsvc
import base64


class catalogo_import(osv.osv_memory):
    _name = 'catalogo.import'
    _description = 'Importa pedidos'

    _columns = {
        # 'filename_po': fields.char('Filename', required=True),
	'filename_catalogo': fields.binary(string='Catalogo Filename'),
        'first_row_column': fields.boolean('1st Row Column Names'),
    }

    _defaults = {
	'first_row_column': True,
	}

    def catalogo_import(self, cr, uid, ids, context=None):

	res = self.read(cr,uid,ids,['filename_catalogo'])
	filename_catalogo = res[0]['filename_catalogo']
	res_first_row = self.read(cr,uid,ids,['first_row_column'])
	first_row = res_first_row[0]['first_row_column']

	if not filename_catalogo:
		raise osv.except_osv(_('Error!'), _("Debe ingresar un archivo a importar!!!"))
		return {'type': 'ir.actions.act_window_close'}

	file=base64.decodestring(filename_catalogo)
	lines=file.split('\n')

	#try:
        #	file = open(filename_po,'r')   # Trying to create a new file or open one
	#except:
	#	raise osv.except_osv(_('Error!'), _("No se puede leer el archivo indicado!!!"))
	#	return {'type': 'ir.actions.act_window_close'}

	#lines = file.readlines()
	index = 1
	dict_orders = {}	
	for line in lines:
		if ((index > 1 and first_row) or (index > 0 and not first_row)):
			cadena = line.split(',')
			if len(cadena)==2:
				supplier_name = cadena[0]
				isbn = cadena[1].replace('\n','')
		
				supplier_id = self.pool.get('res.partner').search(cr,uid,[('name','=',supplier_name)])	
				if not supplier_id:
					raise osv.except_osv(_('Error!'), _("Linea "+str(index)+" .No se encuentra el proveedor "+supplier_isbn))
					return {'type': 'ir.actions.act_window_close'}
				supplier_id = supplier_id[0]
				product_id = self.pool.get('product.product').search(cr,uid,[('ean13','=',isbn)])	
				if not product_id:
					raise osv.except_osv(_('Error!'), _("Linea "+str(index)+" .No se encuentra el producto "+isbn))
					return {'type': 'ir.actions.act_window_close'}
				product_obj = self.pool.get('product.product').browse(cr,uid,product_id)
				tmpl_id = product_obj[0].product_tmpl_id.id
				product_supplier_id = self.pool.get('product.supplierinfo').search(cr,uid,[('name','=',supplier_id),\
					('product_tmpl_id','=',tmpl_id)])
				product_id = product_id[0]
				if not product_supplier_id:
					vals_prod_sup = {
						'name': supplier_id,
						'product_tmpl_id': tmpl_id,
						}
					prod_sup_id = self.pool.get('product.supplierinfo').create(cr,uid,vals_prod_sup)		
        return {}

catalogo_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
