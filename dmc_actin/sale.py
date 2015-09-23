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
class sale_order(osv.osv):
	_inherit="sale.order"
	_columns = {
		'port_load_id': fields.many2one('option.list','Port of loading', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'port_discharge_id': fields.many2one('option.list','Port of discharge', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'deliver_memo': fields.char('DELIVERY DATES'),
		'ship_type': fields.many2one('option.list','SHIPMENT TYPE', ondelete='restrict', domain=[('option_name','=','ship_type')]),
		#fixed content fields
		'terms_fix': fields.text('Fix terms'),	
	}
	def onchange_partner_id(self, cr, uid, ids, part, context=None):
		resu = super(sale_order, self).onchange_partner_id(cr, uid, ids, part, context=context)
		customer = self.pool['res.partner'].browse(cr, uid, part, context=context)
		if customer.port:
			resu['value'].update({'port_discharge_id':customer.port.id})
		if customer.incoterm_id:
			resu['value'].update({'incoterm':customer.incoterm_id.id})
		
		return resu
	def print_sale_offer(self, cr, uid, ids, context=None):
		line_ids = []
		for so in self.browse(cr, uid, ids, context=context):
			line_ids.extend([line.id for line in so.order_line])

		datas = {
				 'model': 'sale.order.line',
				 'ids': line_ids,
#				 'form': self.pool['sale.order.line'].read(cr, uid, line_ids[0], context=context),
		}
		return {'type': 'ir.actions.report.xml', 'report_name': 'sale.offer', 'datas': datas, 'nodestroy': True}
		
	def _prepare_invoice(self, cr, uid, order, lines, context=None):
		invoice_vals = super(sale_order,self)._prepare_invoice(cr, uid, order, lines, context)
		#set invoice other values
		invoice_vals.update({'port_load_id':order.port_load_id and order.port_load_id.id or False,
							'port_discharge_id':order.port_discharge_id and order.port_discharge_id.id or False})
		return invoice_vals		
#po_super.STATE_SELECTION = STATE_SELECTION_PO	