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

class sale_order(osv.osv):
	_inherit = 'sale.order'	
	def action_invoice_create(self, cr, uid, ids, grouped=False, states=None, date_invoice = False, context=None):
		inv_id = super(sale_order, self).action_invoice_create(cr, uid, ids, grouped, states, date_invoice, context)
		pack_obj = self.pool['account.invoice.pack']
		for line in self.pool['account.invoice'].browse(cr, uid, inv_id, context=context).invoice_line:		
			prod_weight_net = 0
			prod_weight_net = 0
			prod_volume = 0
			try:
				prod_weight = float(line.product_id.weight_char)
				prod_weight_net = float(line.product_id.weight_net_char)
				prod_volume = float(line.product_id.volume_char)
			except Exception, e:
				pass
				
			qty_per_carton = line.product_id.qty_per_outer
			qty_carton = qty_per_carton>0 and math.floor(line.quantity/qty_per_carton) or 0
			
			quantity = 0
			if qty_carton > 0:
				#only when the quantity can fill at least 1 carton then execute following code
				quantity = qty_carton * qty_per_carton
							
				weight_net = prod_weight*quantity
				weight_gross = prod_weight_net*quantity
				m3 = prod_volume*quantity
						
				pack_val = {
					'invoice_id': inv_id,
					'sequence': line.sequence,
					'product_id': line.product_id.id or False,				
					'name': line.name,				
					'qty_per_carton': qty_per_carton,
					'qty_carton': qty_carton,
					'quantity': quantity,
					'uos_id': line.uos_id.id,
					'weight_net': weight_net,
					'weight_gross': weight_gross,
					'm3': m3,
					'inv_line_id':line.id
				}			
				pack_obj.create(cr, uid, pack_val, context=context)
			else:
				quantity = 0
			if line.quantity - quantity > 0:
				qty_carton = 1
				quantity = line.quantity - quantity							
				weight_net = prod_weight_net*quantity
				weight_gross = prod_weight*quantity
				m3 = prod_volume*quantity
						
				pack_val = {
					'invoice_id': inv_id,
					'sequence': line.sequence,
					'product_id': line.product_id.id or False,				
					'name': line.name,				
					'qty_per_carton': qty_per_carton,
					'qty_carton': qty_carton,
					'quantity': quantity,
					'uos_id': line.uos_id.id,
					'weight_net': weight_net,
					'weight_gross': weight_gross,
					'm3': m3,
					'inv_line_id':line.id
				}			
				pack_obj.create(cr, uid, pack_val, context=context)

			
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
			for line in order.pack_line:
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
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['pack_line'], 10),
                'account.invoice.pack': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'weight_net_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['pack_line'], 10),
                'account.invoice.pack': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'weight_gross_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['pack_line'], 10),
                'account.invoice.pack': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),
    'm3_total': fields.function(_amount_packing, digits_compute=dp.get_precision('Product UoS'), string='Total',
            store={
                'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['pack_line'], 10),
                'account.invoice.pack': (_get_pack, ['qty_carton', 'weight_net', 'weight_gross', 'm3'], 10),
            },multi='sums'),    
	'pack_line': fields.one2many('account.invoice.pack', 'invoice_id', 'Packing Lines', readonly=True, states={'draft':[('readonly',False)]}),			
	}
								
	
class account_invoice_pack(osv.osv):
	_name="account.invoice.pack"
	_columns = {
		'invoice_id': fields.many2one('account.invoice', 'Invoice Reference', ondelete='cascade', select=True),
		'sequence': fields.integer('Sequence', help="Gives the sequence of this line when displaying the invoice."),
		'product_id': fields.many2one('product.product', 'Product', ondelete='set null', select=True),
		'name': fields.text('Description', required=True),
		'qty_per_carton':fields.float('QTY/CTN', digits_compute = dp.get_precision('Product UoS')),
		'qty_carton':fields.integer('Number of CTN'),
		'quantity': fields.float('Quantity', digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
		'uos_id': fields.many2one('product.uom', 'Unit of Measure', ondelete='set null', select=True),
		'weight_net':fields.float('N.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
		'weight_gross':fields.float('G.W. (KGS)', digits_compute = dp.get_precision('Stock Weight')),
		'm3':fields.float('CBM', digits_compute = dp.get_precision('Stock Weight')),
		'company_id': fields.related('invoice_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
		'inv_line_id': fields.many2one('account.invoice.line', 'Invoice line', ondelete='cascade')
	}		

	def product_id_change(self, cr, uid, ids, product, uom_id, qty=0, name='', type='out_invoice',
			partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
			company_id=None, context=None):
		company_id = company_id if company_id is not None else context.get('company_id', False)
		if not partner_id:
			raise osv.except_osv(_('No Partner Defined!'), _("You must first select a partner!"))
		if not product:
			return {'value': {}, 'domain': {'uos_id': []}}

		values = {}
		product = self.pool['product.product'].browse(product)
		values['name'] = product.partner_ref
		if type in ('out_invoice', 'out_refund'):
			if product.description_sale:
				values['name'] += '\n' + product.description_sale
		else:
			if product.description_purchase:
				values['name'] += '\n' + product.description_purchase

		values['uos_id'] = product.uom_id.id
		if uom_id:
			uom = self.env['product.uom'].browse(uom_id)
			if product.uom_id.category_id.id == uom.category_id.id:
				values['uos_id'] = uom_id

		domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}

		return {'value': values, 'domain': domain}	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	