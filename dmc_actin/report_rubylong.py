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
from openerp.tools import resolve_attr
from openerp.addons.dm_base.utils import number2words_en_upper
from xml.sax.saxutils import escape  

def obj_fields_xml(obj, tag_name, field_list):
	data_xml = "<%s>"%(tag_name, )
	for field_name in field_list:
		field_value = None
		if isinstance(field_name, tuple):
			#use another xml field name
			xml_name = field_name[1]
			new_field_name = field_name[0]
			field_value = resolve_attr(obj, new_field_name)
			if len(field_name) == 3 and callable(field_name[2]):
				#need transfer field value
				field_value = field_name[2](field_value)
		else:
			xml_name = field_name.replace('.', '_')
			field_value = resolve_attr(obj, field_name)
		#xml escape
		if isinstance(field_value,(type(u' '),type(' '))):
			field_value = escape(field_value)		
		data_xml += '<%s>%s</%s>'%(xml_name, field_value, xml_name)
			
	data_xml += "</%s>"%(tag_name, )
	#data_xml = data_xml.replace('\n','\\n\\')
	return data_xml

class purchase_order(osv.osv):
	_inherit="purchase.order"
	def _get_rubylong_xml(self, cr, uid, ids, field_names, args, context=None):
		res = {}
		for po_id in ids:
			res[po_id] = ''
		data_xml = ''
		fileHandle = open ( 'C:/0-code/customer/actin/dmc_actin/static/dm_rubylong_po.xml', 'w' )
		fileHandle.write('<xml>')
		for order in self.browse(cr, uid, ids, context=context):
			data_xml = ''
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
						
						'partner_id.name',
						'partner_id.street',
						'partner_id.street2',
						'partner_id.city',
						'partner_id.country_id.name',
						'partner_id.phone',
						'partner_id.contact',
						'partner_id.email',
						
						'name',
						'date_order',
						
						'client_order_ref',
						'port_load_id.name',
						'port_discharge_id.name',
						
						'amount_total',
						('amount_total', 'amount_total_en', number2words_en_upper),
						
						
						
						'deliver_memo',
						'incoterm_id.name',
						'payment_term_id.name',
						'ship_type.name',
						
						'certs',
						'qc_requirement',						
						'load_control',
						'penalties_on_delays',
						'discrepancy',
						'disputes',
						'doc_export',
						'confirmation',
						'artworks',
						'notes',
						
						('pricelist_id.currency_id.symbol','currency_symbol'),						
						('pricelist_id.currency_id.name','currency_name')
						
						]
			data_xml += obj_fields_xml(order, 'header', order_fields)
			
			#detail data
			line_fields = [
						'order_id.id',
						('supplier_prod_name','supplier_item_no'),
						('name','supplier_item_name'),
						'product_qty',
						'product_uom.name',
						'price_unit',
						'price_subtotal',
						('order_id.pricelist_id.currency_id.symbol','currency_symbol')
						]
			
			for line in order.order_line:
				data_xml += obj_fields_xml(line, 'detail', line_fields)
			
			#write data
			#data_xml.replace("\n", "\n\\")
			res[order.id] = data_xml
			fileHandle.write(data_xml)
		fileHandle.write('</xml>')
		fileHandle.close()
		return res
			
	_columns = {
			'rubylong_xml':fields.function(_get_rubylong_xml, type='text', string='Rubylong xml')
			}
	
	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	