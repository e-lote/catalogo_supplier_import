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
    'filename_catalogo': fields.binary(string='Catalogo Filename', required=True),
    'first_row_column': fields.boolean('1st Row Column Names'),
    'lote_id': fields.many2one('elote.lote',string='Lote', required=True)
    }

    _defaults = {
    'first_row_column': True,
    }

    def catalogo_import(self, cr, uid, ids, context=None):

        for wiz in self.browse(cr, uid, ids, context):

            res = self.read(cr,uid,ids,['filename_catalogo'])

            filename_catalogo = wiz.filename_catalogo
            first_row = wiz.first_row_column
            lote_obj = wiz.lote_id

            file=base64.decodestring(filename_catalogo)
            lines=file.split('\n')

            if lote_obj.state != 'draft':
                raise osv.except_osv(_('Error!'), _("El lote seleccionado debe estar en estado borrador!!!"))
                return {'type': 'ir.actions.act_window_close'}
                

            index = 1
            dict_orders = {}
            list_products = []    
            for line in lines:
                if ((index > 1 and first_row) or (index > 0 and not first_row)):
                    cadena = line.split(',')
                    if len(cadena)==3:
                        supplier_name = cadena[0]
                        isbn = cadena[1].replace('\n','')
                        supplier_price = float(cadena[2])
                
                        supplier_id = self.pool.get('res.partner').search(cr,uid,[('name','=',supplier_name)])    
                        if not supplier_id:
                            raise osv.except_osv(_('Error!'), _("Linea "+str(index)+" .No se encuentra el proveedor "+supplier_name))
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
                        list_products.append(product_id)
                        vals_prod_sup = {
                            'name': supplier_id,
                            'product_tmpl_id': tmpl_id,
                            'min_qty': 1,
                            'lote_id': lote_obj.id,
                            }
                        if not product_supplier_id:
                            vals_prod_sup['supplier_price'] = supplier_price
                            prod_sup_id = self.pool.get('product.supplierinfo').create(cr,uid,vals_prod_sup)
                        else:
                            vals_prod_sup['valid_to'] = str(date.today())
                            return_id = self.pool.get('product.supplierinfo').write(cr,uid,product_supplier_id,vals_prod_sup)
                            del vals_prod_sup['valid_to']
                            vals_prod_sup['supplier_price'] = supplier_price
                            return_id = self.pool.get('product.supplierinfo').create(cr,uid,vals_prod_sup)
                index += 1
            if not list_products:
                raise osv.except_osv(_('Error!'), _("Linea "+str(index)+"Vacia lista list_products ."))
                return {'type': 'ir.actions.act_window_close'}
                
                vals_lote = {
                       'product_ids': [(6, 0, list_products)],
                        }
                return_id = self.pool.get('elote.lote').write(cr,uid,lote_id,vals_lote)

                
        return {}

catalogo_import()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
