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

class sale_order(osv.osv):
	_inherit="sale.order"
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
			#header data
			order_fields = [
						('id','order_id'),
						'company_id.name',
						'company_id.street',
						'company_id.street2',
						'company_id.city',
						'company_id.country_id.name',
						'company_id.contact',
						'company_id.phone',
						'company_id.fax',
						'company_id.email',
						('company_id.logo','company_logo'),
						
						'partner_invoice_id.name',
						('partner_invoice_id.name', 'partner_invoice_id_name_upper', upper),
						'partner_invoice_id.street',
						'partner_invoice_id.street2',
						'partner_invoice_id.city',
						'partner_invoice_id.country_id.name',
						'partner_invoice_id.phone',
						'partner_invoice_id.contact',
						'partner_invoice_id.email',
						
						'partner_shipping_id.name',
						('partner_shipping_id.name', 'partner_invoice_id_name_upper', upper),
						'partner_shipping_id.street',
						'partner_shipping_id.street2',
						'partner_shipping_id.city',
						'partner_shipping_id.country_id.name',
						'partner_shipping_id.phone',
						'partner_shipping_id.contact',
						'partner_shipping_id.email',
						
						'name',
						'date_order',
						
						('client_order_ref','', upper),
						('port_load_id.name','', upper),
						('port_discharge_id.name','', upper),
						
						'amount_total',
						('amount_total', 'amount_total_en', number2words_en_upper2),
						
						'deliver_memo',
						('incoterm.name', 'incoterm_id_name'),
						('payment_term.name','payment_term_id_name'),
						'ship_type.name',
						
						'terms_fix',
						'note',						
						
						'company_id.bank_id.bank_name',
						'company_id.bank_id.street',
						'company_id.bank_id.owner_name',
						'company_id.bank_id.bank_bic',
						'company_id.bank_id.acc_number',
						
						('pricelist_id.currency_id.symbol','currency_symbol'),						
						('pricelist_id.currency_id.name','currency_name'),
						
						#dm added
						('company_id.img_stamp','company_stamp'),
						
						#user added
						('company_id.bank_id.bank_swift','company_id_bank_id_bank_code')				
						
						]
			data_xml += get_rubylong_fields_xml(order, 'header', order_fields)
			
		for order in orders:
			#detail data
			line_fields = [
						('order_id.id','order_id'),
						('id','order_line_id'),
						('cust_prod_code','item_no'),
						('name','item_name'),
						('product_uom_qty','product_qty'),
						'product_uom.name',
						'price_unit',
						'price_subtotal',
						('order_id.pricelist_id.currency_id.symbol','currency_symbol')
						]
			
			for line in order.order_line:
				data_xml += get_rubylong_fields_xml(line, 'detail', line_fields)
		
		#write data
		if order_main:
			res[order_main.id] = get_rublong_data_url(order_main,data_xml,cr.dbname)
		return res
			
	_columns = {
			'rubylong_xml_file':fields.function(_get_rubylong_xml, type='text', string='Rubylong xml')
			}
	
	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	