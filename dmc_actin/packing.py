		# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.openerp.com>
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
import openerp.addons.decimal_precision as dp
import math
class account_invoice_line(osv.osv):
	_inherit="account.invoice.line"
	_columns = {
    'qty_per_carton':fields.float('QTY/CTN', digits_compute = dp.get_precision('Product UoS')),
    'qty_carton':fields.integer('Number of CTN'),
    'weight_net':fields.float('N.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
    'weight_gross':fields.float('G.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
    'm3':fields.float('CBM', digits_compute = dp.get_precision('Stock Weight')),
	}	
	
class sale_order_line(osv.osv):
	_inherit = 'sale.order.line'

	def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
		res = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id=account_id, context=context)
		qty_per_carton = line.product_id.qty_per_outer
		qty_carton = qty_per_carton>0 and math.ceil(line.product_uom_qty/qty_per_carton) or 0
		weight_net = line.product_id.weight_net*line.product_uom_qty
		weight_gross = line.product_id.weight*line.product_uom_qty
		m3 = line.product_id.volume*line.product_uom_qty

		if qty_carton > 0:
			weight_net = line.product_id.pack_out_nw * qty_carton
			weight_gross = line.product_id.pack_out_gw * qty_carton
			m3 = line.product_id.pack_out_volume * qty_carton

		res.update({'qty_per_carton':qty_per_carton,'qty_carton':qty_carton,
				'weight_net':weight_net,'weight_gross':weight_gross,'m3':m3})
		
		return res	

class account_invoice(osv.osv):
	_inherit="account.invoice"
	def _amount_packing(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'qty_carton_total': 0,
				'weight_net_total': 0.0,
				'weight_gross_total': 0.0,
				'm3_total': 0.0,
			}
			for line in order.invoice_line:
				res[order.id]['qty_carton_total'] += line.qty_carton
				res[order.id]['weight_net_total'] += line.weight_net
				res[order.id]['weight_gross_total'] += line.weight_gross
				res[order.id]['m3_total'] += line.m3
		return res

	def _get_pack(self, cr, uid, ids, context=None):
		result = {}
		for line in self.browse(cr, uid, ids, context=context):
			result[line.invoice_id.id] = True
		return result.keys()
	
	_columns = {
    'pack_comment':fields.text('Remarks'),
    'qty_carton_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                'account.invoice.line': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'weight_net_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                'account.invoice.line': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'weight_gross_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                'account.invoice.line': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'm3_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['invoice_line'], 10),
                'account.invoice.line': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),    			
	}
	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	