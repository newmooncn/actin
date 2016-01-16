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
from openerp.addons.purchase.purchase import purchase_order as po_super

from openerp.addons.dm_base.utils import number2words_en_upper, number2words_en_upper2
from string import upper
from openerp.addons.dm_rubylong import get_rubylong_fields_xml, get_rublong_data_url, get_rubylong_fields_xml_body

class account_invoice(osv.osv):
	_inherit="account.invoice"
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
						
						('partner_id.name','partner_invoice_id_name'),
						('partner_id.name', 'partner_invoice_id_name_upper', upper),
						('partner_id.street','partner_invoice_id_street'),
						('partner_id.street2','partner_invoice_id_street2'),
						('partner_id.city','partner_invoice_id_city'),
						('partner_id.country_id.name','partner_invoice_id_country_id_name'),
						('partner_id.phone','partner_invoice_id_phone'),
						('partner_id.contact','partner_invoice_id_contact'),
						('partner_id.email','partner_invoice_id_email'),						
						
						('number','name'),
						('date_invoice','date_order'),						
						
						('port_load_id.name','', upper),
						('port_discharge_id.name','', upper),
						
						'amount_total',
						('amount_total', 'amount_total_en', number2words_en_upper2),

						'total_shipped',
						'contract_n',
						'bl_number',
						'container_no',
						'seal_no',
						'serial_no',
						'hs_code',
						
						('currency_id.symbol','currency_symbol'),						
						('currency_id.name','currency_name'),		
						
						]
			
			order_xml = get_rubylong_fields_xml_body(order, order_fields)
			
			#partner shipping address			
			sale_order = self.sale_order(cr, uid, order.id, context=context)
			if sale_order:
				order_fields = [
							('partner_id.name','partner_shipping_id_name'),
							('partner_id.name', 'partner_shipping_id_name_upper', upper),
							('partner_id.street','partner_shipping_id_street'),
							('partner_id.street2','partner_shipping_id_street2'),
							('partner_id.city','partner_shipping_id_city'),
							('partner_id.country_id.name','partner_shipping_id_country_id_name'),
							('partner_id.phone','partner_shipping_id_phone'),
							('partner_id.contact','partner_shipping_id_contact'),
							('partner_id.email','partner_shipping_id_email'),	
							('client_order_ref','', upper),
							]
				order_xml += get_rubylong_fields_xml_body(sale_order, order_fields)
			
			#add this order's xml
			data_xml = "<%s>%s</%s>"%('header', order_xml, 'header')			
			
		for order in orders:
			#detail data
			line_fields = [
						('invoice_id.id','order_id'),
						('id','order_line_id'),
						('sale_line_id.cust_prod_code','item_no'),
						('name','item_name'),
						('quantity','product_qty'),
						('uos_id.name','product_uom_name'),
						'price_unit',
						'price_subtotal',
						('invoice_id.currency_id.symbol','currency_symbol')
						]
			
			for line in order.invoice_line:
				data_xml += get_rubylong_fields_xml(line, 'detail', line_fields)
		
		#write data
		if order_main:
			res[order_main.id] = get_rublong_data_url(order_main,data_xml,cr.dbname)
		return res
			
	_columns = {
			'rubylong_xml_file':fields.function(_get_rubylong_xml, type='text', string='Rubylong xml')
			}
	
	def sale_order(self, cr, uid, inv_id, context=None):
		inv = self.browse(cr, uid, inv_id, context=context)
		so = inv.sale_ids and inv.sale_ids[0] or False
		#origin_inv_id is from invoice_refund.py
		if not so and inv.origin_inv_id:
			#for customer refund / credit note
			so = self.sale_order(cr, uid, inv.origin_inv_id, context=context)
		return so	
	
class account_invoice_line(osv.Model):
	_inherit = 'account.invoice.line'
	_columns = {
        'sale_line_id': fields.many2one('sale.order.line',
            'Sale Order Line', ondelete='set null', select=True,
            readonly=True),
    }

class sale_order_line(osv.Model):
	_inherit = 'sale.order.line'
	def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False, context=None):
		vals = super(sale_order_line, self)._prepare_order_line_invoice_line(cr, uid, line, account_id, context=context)
		vals['sale_line_id'] = line.id
		return vals
#po_super.STATE_SELECTION = STATE_SELECTION_PO	