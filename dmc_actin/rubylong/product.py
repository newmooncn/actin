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

from openerp.addons.dm_base.utils import number2words_en_upper, number2words_en_upper2
from string import upper
from openerp.addons.dm_rubylong import get_rubylong_fields_xml, get_rublong_data_url

class product_product(osv.osv):
	_inherit = "product.product"
	
	rbfields_base = [
						('id','product_id'),
						'company_id.name',
						'company_id.street',
						'company_id.street2',
						'company_id.city',
						'company_id.zip',
						'company_id.country_id.name',
						'company_id.contact',
						'company_id.phone',
						'company_id.fax',
						'company_id.email',
						('company_id.logo','company_logo'),
						
						('name','',upper),
						('default_code','code'),
						'image',
						'description',
						
						'tech_data',
						
						'certificate',
						'labor',
						
						'dimension',
						('weight_char','weight_gross'),
						('weight_net_char','weight_net'),
						'pack_out_dimension',
						'pack_out_volume',
						('pack_out_gw','pack_out_weight_gross'),
						
						'qty_20gp',
						'qty_40gp',
						'qty_40hq',
						'qty_pallet_eur',
						'qty_pallet_us',
                        
                        'quote_validity',
                        'additional_comments',					
						
						]

	def _get_rubylong_xml(self, cr, uid, ids, field_names, args, context=None):
		if isinstance(ids, (int, long)):
			ids = [ids]
		res = {}
		for po_id in ids:
			res[po_id] = ''
		data_xml = ''
		order_main = None
		orders = self.browse(cr, uid, ids, context=context)
		for order in orders:
			if not order_main:
				order_main = order
			#base data
			order_fields = self.rbfields_base
			data_xml += get_rubylong_fields_xml(order, 'header', order_fields)
		
		#write data
		if order_main:
			res[order_main.id] = get_rublong_data_url(order_main,data_xml,cr.dbname)
		return res
			
	_columns = {
			'rubylong_xml_file':fields.function(_get_rubylong_xml, type='text', string='Rubylong xml'),
			}	