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
class account_invoice_line(osv.osv):
	_inherit="account.invoice.line"
	_columns = {
    'qty_per_carton':fields.float('QTY/CTN', digits_compute = dp.get_precision('Product UoS')),
    'qty_carton':fields.integer('CTN'),
    'weight_net':fields.float('N.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
    'weight_gross':fields.float('G.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
    'm3':fields.float('M3', digits_compute = dp.get_precision('Stock Weight')),
	}
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