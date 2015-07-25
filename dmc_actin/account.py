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
class purchase_order(osv.osv):
	_inherit="purchase.order"
	#'Draft PO'==>'Quotation', 'Purchase Confirmed'==>'Purchase Order'
	STATE_SELECTION = [
		('draft', 'Quotation'),
		('sent', 'RFQ'),
		('bid', 'Bid Received'),
		('confirmed', 'Waiting Approval'),
		('approved', 'Purchase Order'),
		('except_picking', 'Shipping Exception'),
		('except_invoice', 'Invoice Exception'),
		('done', 'Done'),
		('cancel', 'Cancelled')
	]
	
	_columns = {
		'client_order_ref': fields.char('Customer PO Ref', copy=False),
		'port_load_id': fields.many2one('option.list','Port of loading', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'port_discharge_id': fields.many2one('option.list','Port of discharge', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'deliver_memo': fields.char('DELIVERY DATES'),
		'ship_type': fields.many2one('option.list','SHIPMENT TYPE', ondelete='restrict', domain=[('option_name','=','ship_type')]),
		#fixed content fields
		'certs': fields.text('CERTIFICATIONS'),
		'qc_requirement': fields.text('QUALITY CONTROL REQUIREMENTS'),
		'load_control': fields.text('LOADING CONTROL REQUIREMENTS'),
		'penalties_on_delays': fields.text('PENALTIES ON DELAYS'),
		'discrepancy': fields.text('DISCREPANCY'),
		'disputes': fields.text('DISPUTES'),
		'doc_export': fields.text('DOCUMENTS EXPORT'),
		'confirmation': fields.text('CONFIRMATION'),
		'artworks': fields.text('ARTWORKS'),
		#redefine since the status name changed
		'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
								  help="The status of the purchase order or the quotation request. "
									   "A request for quotation is a purchase order in a 'Draft' status. "
									   "Then the order has to be confirmed by the user, the status switch "
									   "to 'Confirmed'. Then the supplier must confirm the order to change "
									   "the status to 'Approved'. When the purchase order is paid and "
									   "received, the status becomes 'Done'. If a cancel action occurs in "
									   "the invoice or in the receipt of goods, the status becomes "
									   "in exception.",
								  select=True, copy=False),	
		#link to sale order
		'sale_id':fields.many2one('sale.order','Sales Offer')	
	}
	def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
		resu = super(purchase_order, self).onchange_partner_id(cr, uid, ids, partner_id, context=context)
		customer = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
		if customer.port:
			resu['value'].update({'port_load_id':customer.port.id})
		if customer.incoterm_id:
			resu['value'].update({'incoterm_id':customer.incoterm_id.id})
		
		return resu
		
	def gen_sale_order(self, cr, uid, ids, context=None):
		assert len(ids) == 1, 'Only one quotation can be select to generate sales order'
		po = self.browse(cr, uid, ids[0], context=context)
		#===========prepare sale_order===================
		so_val = {}
		sale_obj = self.pool['sale.order']
		#update customer
		customer_id = None
		for po_line in po.order_line:
			if po_line.product_id.customer_id:
				customer_id = po_line.product_id.customer_id.id
				break
		if not customer_id:
			raise osv.except_osv(_('Error'),'Please define customer for the products!')
		so_val = {'partner_id':customer_id}
		#update partner_invoice_id/partner_shipping_id/payment_term/fiscal_position/pricelist_id/port_discharge_id/incoterm
		so_val.update(sale_obj.onchange_partner_id(cr, uid, [], customer_id, context=context)['value'])
		#copy values from purchase order
		so_val.update({'client_order_ref':po.client_order_ref, 'port_load_id':po.port_discharge_id.id})
		so_id = sale_obj.create(cr, uid, so_val, context=context)
		self.write(cr, uid, ids, {'sale_id':so_id}, context=context)
		#===========prepare sale_order_line===================
		sale_line_obj = self.pool['sale.order.line']
		for po_line in po.order_line:
			so_line_val = {'order_id':so_id, 'product_id': po_line.product_id.id, 'product_uom_qty':po_line.product_qty, 'price_unit':po_line.price_unit}
			line_vals = sale_line_obj.product_id_change(cr, uid, [], so_val['pricelist_id'], po_line.product_id.id, partner_id=customer_id, context=None)
			so_line_val.update(line_vals['value'])
			sale_line_obj.create(cr, uid, so_line_val, context=context)
		#===========goto sale order form page===================
		form_view = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
		form_view_id = form_view and form_view[1] or False
		return {
			'name': _('Sale Quotations'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [form_view_id],
			'res_model': 'sale.order',
			'type': 'ir.actions.act_window',
			'target': 'current',
			'res_id': so_id,
		}
	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	