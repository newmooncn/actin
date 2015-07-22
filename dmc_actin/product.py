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
		'tech_data':  fields.text('Technical data'),
		'certificate': fields.text('Certifications'),
		'labor': fields.text('Laboratory'),
		
		'dimension': fields.char('Dimensions', size=64),
#		'pack_type': fields.selection([('carton','Carton box'), ('blister','Blister'),('others','Others')], string='Packing type'),
		'pack_type': fields.many2one('option.list','Packing type', ondelete='restrict', domain=[('option_name','=','pack_type')]),
		#for pack type 'Others' memo
		'pack_type_memo': fields.char('Packing Type Note', size=64),
		
		'pack_out_dimension': fields.char('Outer packing dimensions', size=64),
		'pack_out_volume': fields.float('Outer packing volume'),
		'pack_out_nw': fields.float('Outer packing NW'),
		'pack_out_gw': fields.float('Outer packing GW'),
		
		'pack_inner_dimension': fields.char('Inner Carton packing dimensions', size=64),
		'pack_inner_volume': fields.float('Inner packing volume'),
		'pack_inner_nw': fields.float('Inner Carton Packing NW'),
		'pack_inner_gw': fields.float('Inner Carton Packing GW'),
		
		'number_inner_outer': fields.integer('Number of Inner per Outer'),
		
		'qty_pallet_eur': fields.integer('Quantity per pallet EUROPE (0.8 x 1m)'),		
		'qty_pallet_us': fields.integer('Quantity per pallet AMERICAN (1 x 1.2m)'),
		'qty_20gp': fields.integer('Quantity per 20''GP'),
		'qty_40gp': fields.integer('Quantity per 40''GP'),
		'qty_40hq': fields.integer('Quantity per 40''HQ'),
		
		'hs_code': fields.char('HS code', size=32),
		'additional_comments':fields.text('Additional comments'),
		
		#for factory/supplier
		'moq': fields.integer('MOQ'),
		'seller_sample_price': fields.float('Samle price'),
		'seller_sample_lead_time': fields.integer('Sample lead time'),
		'seller_lead_time': fields.integer('Leadtime'),
		'quote_validity': fields.integer('Quotation validity')
	}
#	_defaults = {'type':'service'}
				
product_product()