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

class product_product(osv.osv):
	_inherit = "product.product"
	_columns = {
		'tech_data':  fields.text('Technical specifications'),
		'certificate': fields.text('Certifications'),
		'labor': fields.text('Laboratory'),
		
		'dimension': fields.char('Dimensions', size=64),
#		'pack_type': fields.selection([('carton','Carton box'), ('blister','Blister'),('others','Others')], string='Packing type'),
		'pack_type': fields.many2one('option.list','Packing type', ondelete='restrict', domain=[('option_name','=','pack_type')]),
		#for pack type 'Others' memo
		'pack_type_memo': fields.char('Packing Type Note', size=64),
		
		'pack_out_dimension': fields.char('Outer packing dimensions (meters)', size=64),
		'pack_out_volume': fields.float('Outer packing volume (cbm)'),
		'pack_out_nw': fields.float('Outer packing NW (kgs)'),
		'pack_out_gw': fields.float('Outer packing GW (kgs)'),
		
		'pack_inner_dimension': fields.char('Inner Carton packing dimensions(meters)', size=64),
		'pack_inner_volume': fields.float('Inner packing volume(cbm)'),
		'pack_inner_nw': fields.float('Inner Carton Packing NW(kgs)'),
		'pack_inner_gw': fields.float('Inner Carton Packing GW(kgs)'),
		
		'qty_per_inner': fields.integer('Quantity per Inner'),
		'number_inner_outer': fields.integer('Number of Inner per Outer'),
		'qty_per_outer': fields.integer('Quantity per Outer'),
		
		'qty_pallet_eur': fields.integer('Quantity per pallet EUROPE (0.8 x 1m)'),		
		'qty_pallet_us': fields.integer('Quantity per pallet AMERICAN (1 x 1.2m)'),
		'qty_20gp': fields.integer('Quantity per 20''GP'),
		'qty_40gp': fields.integer('Quantity per 40''GP'),
		'qty_40hq': fields.integer('Quantity per 40''HQ'),
		
		'hs_code': fields.char('HS code', size=32),
		'hs_code_tax_rate': fields.float('Tax rate', size=32),
		'additional_comments':fields.text('Additional comments'),
		
		#for factory/supplier
		'moq': fields.integer('MOQ'),
		'seller_sample_price': fields.float('Sample price', digits_compute= dp.get_precision('Product Price')),
		'seller_sample_lead_time': fields.integer('Sample lead time'),
		'seller_lead_time': fields.integer('Leadtime'),
		'quote_validity': fields.integer('Quotation validity'),
		
		#currency for cost price
		'standard_price_curr_id': fields.many2one('res.currency', 'Currency',),
		
		#fields for supplier
		'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm'),
		'port_load': fields.many2one('option.list','Loading Port', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'seller_payment_term_id': fields.many2one('account.payment.term',string ='Payment Terms'),
	}
	#For ACTIN, product code must be entered manually
	_defaults = {'default_code':''}
	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if not vals.get('default_code') or vals.get('default_code')=='/':
			raise osv.except_osv('Error!', 'Product code is required for new product!')
		return super(product_product, self).create(cr, uid, vals, context)
	
	def _check_write_vals(self,cr,uid,vals,ids=None,context=None):
		if vals.get('default_code') and vals['default_code']:
			vals['default_code'] = vals['default_code'].strip()
			if ids:
				product_id = self.search(cr, uid, [('default_code', '=', vals['default_code']),('id','not in',ids)])
			else:
				product_id = self.search(cr, uid, [('default_code', '=', vals['default_code'])])
			if product_id:
				raise osv.except_osv(_('Error!'), _('Product code must be unique!'))
		if vals.get('cn_name'):
			vals['cn_name'] = vals['cn_name'].strip()
			if ids:
				product_id = self.search(cr, uid, [('cn_name', '=', vals['cn_name']),('id','not in',ids)])
			else:
				product_id = self.search(cr, uid, [('cn_name', '=', vals['cn_name'])])
			if product_id:
				raise osv.except_osv(_('Error!'), _('Product Chinese Name must be unique!'))
		#for ACTIN logic, the product name may be duplicated, the product code unique is enough
#		if vals.get('name'):
#			vals['name'] = vals['name'].strip()
#			if ids:
#				product_id = self.search(cr, uid, [('name', '=', vals['name']),('id','not in',ids)])
#			else:
#				product_id = self.search(cr, uid, [('name', '=', vals['name'])])
#			if product_id:
#				raise osv.except_osv(_('Error!'), _('Product Name must be unique!'))		
		return True
	
	def onchange_dimension(self, cr, uid, ids, dimension, field_volume, context=None):
		if dimension:
			try:
				volume = eval(dimension)
			except Exception, e:
				volume = 0.0
		else:
			volume = 0.0				
		return {'value': {field_volume: volume}}	

class product_template(osv.osv):
	_inherit = "product.template"
	_columns = {		
		#change volume, gross weight, net weight to text fields, user want to input UOM name in them
		'volume_char': fields.char('Volume'),
        'weight_char': fields.char('Gross Weight'),
        'weight_net_char': fields.char('Net Weight'),
	}
				

class product_customerinfo(osv.osv):
	_inherit = "product.customerinfo"
	_columns = {
		'payment_term_id': fields.many2one('account.payment.term',string ='Payment Terms'),
		'port_discharge': fields.many2one('option.list','Destination Port', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'curr_name': fields.char('Currency'),
		'ean13': fields.char('EAN13', size=13),
        'incoterm': fields.many2one('stock.incoterms', 'Incoterm'),
    }
	_defaults={'curr_name':'USD'}