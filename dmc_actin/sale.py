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
import time
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

class sale_order(osv.osv):
	
	_inherit="sale.order"
	_columns = {
		'state': fields.selection([
			('draft', 'Draft Quotation'),
			('sent', 'Quotation Sent'),
			('cancel', 'Cancelled'),
			('waiting_date', 'Waiting Schedule'),
			#johnw, 09/29/2015, reverse the sequence of manual and progress
#			('progress', 'Sales Order'),
#			('manual', 'Sale to Invoice'),
			('manual', 'Sale to Invoice'),
			('progress', 'Sales Order'),
			('shipping_except', 'Shipping Exception'),
			('invoice_except', 'Invoice Exception'),
			('done', 'Done'),
			], 'Status', readonly=True, copy=False, help="Gives the status of the quotation or sales order.\
			  \nThe exception status is automatically set when a cancel operation occurs \
			  in the invoice validation (Invoice Exception) or in the picking list process (Shipping Exception).\nThe 'Waiting Schedule' status is set when the invoice is confirmed\
			   but waiting for the scheduler to run on the order date.", select=True),
						
		'port_load_id': fields.many2one('option.list','Port of loading', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'port_discharge_id': fields.many2one('option.list','Port of discharge', ondelete='restrict', domain=[('option_name','=','partner_port')]),
		'deliver_memo': fields.char('DELIVERY DATES'),
		'ship_type': fields.many2one('option.list','Shipment Type', ondelete='restrict', domain=[('option_name','=','ship_type')]),
		#fixed content fields
		'terms_fix': fields.text('Fix terms'),	
	}

	def write(self, cr, uid, ids, vals, context=None):
		resu = super(sale_order,self).write(cr, uid, ids, vals, context=context)		
		if 'partner_id' in vals:
			#update line's price and customer product reference to new customer's
			prod_obj = self.pool['product.product']
			soln_obj = self.pool['sale.order.line']
			for order in self.browse(cr, uid, ids, context=context):
				incoterm_new_id = None
				for line in order.order_line:
					cust_prod = prod_obj.get_customer_product(cr, uid, vals['partner_id'], line.product_id.id, context=context)
					if cust_prod:
						soln_obj.write(cr, uid, [line.id],{'price_unit':cust_prod.price, 'cust_prod_code':cust_prod.product_code, 'name':cust_prod.product_name or ' '}, context=context)
						if cust_prod.incoterm and not incoterm_new_id:
							incoterm_new_id = cust_prod.incoterm.id		
				if incoterm_new_id:
					self.write(cr, uid, [order.id],{'incoterm':incoterm_new_id},context=context)								
		return resu
	
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
							'port_discharge_id':order.port_discharge_id and order.port_discharge_id.id or False,
							'name':order.name})
		return invoice_vals		
	
	#add function for 'set to draft' button, 11/06/2015   
	def action_cancel_draft(self, cr, uid, ids, context=None):
		if not len(ids):
			return False
		self.write(cr, uid, ids, {'state':'draft'})
		self.set_order_line_status(cr, uid, ids, 'draft', context=context)
		for p_id in ids:
			# Deleting the existing instance of workflow for PO
			self.delete_workflow(cr, uid, [p_id]) # TODO is it necessary to interleave the calls?
			self.create_workflow(cr, uid, [p_id])
		return True
	
	def set_order_line_status(self, cr, uid, ids, status, context=None):
		line = self.pool.get('sale.order.line')
		order_line_ids = []
		proc_obj = self.pool.get('procurement.order')
		for order in self.browse(cr, uid, ids, context=context):
			if status in ('draft', 'cancel'):
				order_line_ids += [po_line.id for po_line in order.order_line]
			else: # Do not change the status of already cancelled lines
				order_line_ids += [po_line.id for po_line in order.order_line if po_line.state != 'cancel']
		if order_line_ids:
			line.write(cr, uid, order_line_ids, {'state': status}, context=context)
		if order_line_ids and status == 'cancel':
			procs = proc_obj.search(cr, uid, [('sale_line_id', 'in', order_line_ids)], context=context)
			if procs:
				proc_obj.write(cr, uid, procs, {'state': 'cancel'}, context=context)
		return True	
	
from openerp.addons.sale.sale import sale_order_line as so_line_super	

def product_id_change_so_actin(self, cr, uid, ids, pricelist, product, qty=0,
		uom=False, qty_uos=0, uos=False, name='', partner_id=False,
		lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):

	context = context or {}
	lang = lang or context.get('lang', False)
	if not partner_id:
		raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
	warning = False
	product_uom_obj = self.pool.get('product.uom')
	partner_obj = self.pool.get('res.partner')
	product_obj = self.pool.get('product.product')
	partner = partner_obj.browse(cr, uid, partner_id)
	lang = partner.lang
	context_partner = context.copy()
	context_partner.update({'lang': lang, 'partner_id': partner_id})

	if not product:
		return {'value': {'th_weight': 0,
			'product_uos_qty': qty}, 'domain': {'product_uom': [],
			   'product_uos': []}}
	if not date_order:
		date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

	result = {}
	warning_msgs = ''
	product_obj = product_obj.browse(cr, uid, product, context=context_partner)

	uom2 = False
	if uom:
		uom2 = product_uom_obj.browse(cr, uid, uom)
		if product_obj.uom_id.category_id.id != uom2.category_id.id:
			uom = False
	if uos:
		if product_obj.uos_id:
			uos2 = product_uom_obj.browse(cr, uid, uos)
			if product_obj.uos_id.category_id.id != uos2.category_id.id:
				uos = False
		else:
			uos = False

	fpos = False
	if not fiscal_position:
		fpos = partner.property_account_position or False
	else:
		fpos = self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position)
	if update_tax: #The quantity only have changed
		result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

	'''
	johnw,2015/12/08, comment the name's getting logic, use product customer name as name
	if not flag:
		result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
		if product_obj.description_sale:
			#johnw, 10/21/2015, change the name to be the product.description_sale
			#result['name'] += '\n'+product_obj.description_sale
			result['name'] = product_obj.description_sale
	'''
	domain = {}
	if (not uom) and (not uos):
		result['product_uom'] = product_obj.uom_id.id
		if product_obj.uos_id:
			result['product_uos'] = product_obj.uos_id.id
			result['product_uos_qty'] = qty * product_obj.uos_coeff
			uos_category_id = product_obj.uos_id.category_id.id
		else:
			result['product_uos'] = False
			result['product_uos_qty'] = qty
			uos_category_id = False
		result['th_weight'] = qty * product_obj.weight
		domain = {'product_uom':
					[('category_id', '=', product_obj.uom_id.category_id.id)],
					'product_uos':
					[('category_id', '=', uos_category_id)]}
	elif uos and not uom: # only happens if uom is False
		result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
		result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
		result['th_weight'] = result['product_uom_qty'] * product_obj.weight
	elif uom: # whether uos is set or not
		default_uom = product_obj.uom_id and product_obj.uom_id.id
		q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
		if product_obj.uos_id:
			result['product_uos'] = product_obj.uos_id.id
			result['product_uos_qty'] = qty * product_obj.uos_coeff
		else:
			result['product_uos'] = False
			result['product_uos_qty'] = qty
		result['th_weight'] = q * product_obj.weight		# Round the quantity up

	if not uom2:
		uom2 = product_obj.uom_id
	# get unit price

	if not pricelist:
		warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
				'Please set one before choosing a product.')
		warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
	else:
		ctx = dict(
			context,
			uom=uom or result.get('product_uom'),
			date=date_order,
		)
		price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
				product, qty or 1.0, partner_id, ctx)[pricelist]
		if price is False:
			warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
					"You have to change either the product, the quantity or the pricelist.")

			warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
		else:
			result.update({'price_unit': price})
			if context.get('uom_qty_change', False):
				return {'value': {'price_unit': price}, 'domain': {}, 'warning': False}
	if warning_msgs:
		warning = {
				   'title': _('Configuration Error!'),
				   'message' : warning_msgs
				}
	#add customer product price, johnw, 2015/10/21
	#add customer product reference, johnw, 2015/10/28
	cust_prod = self.pool['product.product'].get_customer_product_info(cr, uid, partner_id, product, context=context)
	if cust_prod:
		result.update({'price_unit':cust_prod['price']})
		result.update({'cust_prod_code':cust_prod['product_code']})
		#add customer product name to SO's description
		if cust_prod['product_name']:
			#johnw, 2015/12/08, use product customer name as name
			#result['name'] = '%s %s'%(cust_prod['product_name'], result.get('name',''))
			#result['name'] = result['name'].strip()
			result['name'] = cust_prod['product_name']
	if not result.get('name'):
		result['name'] = ' '
	return {'value': result, 'domain': domain, 'warning': warning}

so_line_super.product_id_change = product_id_change_so_actin

class sale_order_line(osv.osv):
	_inherit="sale.order.line"
	_columns = {'cust_prod_code': fields.char('Customer Product Reference', size=64),}
#po_super.STATE_SELECTION = STATE_SELECTION_PO	