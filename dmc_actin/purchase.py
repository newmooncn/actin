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
	}
	

	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	