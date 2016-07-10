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

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
class account_invoice(models.Model):
	_inherit="account.invoice"
	# set readonly only to false when paid
	supplier_invoice_number = fields.Char(string='Supplier Invoice Number',
		help="The reference of this invoice as provided by the supplier.",
		readonly=False, states={'paid': [('readonly', True)]})
		
	name = fields.Char(string='Reference/Description', index=True,
	        readonly=True, states={'draft': [('readonly', False)]})
	
	#new fields on PDF
	total_shipped = fields.Char('TOTAL SHIPPED', size=64)
	contract_n = fields.Char('CONTRACT NUMBER', size=64)
	bl_number = fields.Char('BL NUMBER', size=64)
	container_no = fields.Char('CONTAINER NUMBER', size=64)
	seal_no = fields.Char('SEAL NUMBER', size=64)
	serial_no = fields.Text('SERIAL NUMBER')
	hs_code = fields.Char('HS CODE', size=64)
	#new fields for estimated deliver an arrival
	etd = fields.Date('ETD')
	eta = fields.Date('ETA')
	#used for service invoice, related to the commercial invoice
	ci_service_type = fields.Selection(selection=(('trans_sea','TPS Sea Freight'),
												('trans_dc','TPS Destination charge'),
												('logistics','Logistics'),
												('quanlity','Quality control'),
												('laboratory','Laboratory'),
												('audit','Audit'),
												('accounting','Accounting'),
												('procurement','Procurement'),
												('sourcing','Sourcing'),
												('others','Others')),
									string='Service type')		 

	parent_id = fields.Many2one('account.invoice', 'Commercial Invoice', select=True, domain="[('is_service','=',False),('type','=','out_invoice')]")	
	child_ids = fields.One2many('account.invoice', 'parent_id', 'Service Invoices')
	
	#fields for loading/discharge ports, #will be set in sale.py._prepare_invoice()
	port_load_id = fields.Many2one('option.list', string='Port of loading', domain=[('option_name','=','partner_port')])
	port_discharge_id = fields.Many2one('option.list', string='Port of discharge', domain=[('option_name','=','partner_port')])
	
	#fields for the service flag
	is_service = fields.Boolean('Service')
	
	#addiontional for CN/DN, johnw, 2016/06/12, the original 'comment' field is used for "sales/purchase journal description"
	addion_comment = fields.Char('Additional Information')
	
	#add incoterm, johnw, 2016/07/10
	incoterm = fields.Many2one('stock.incoterms', string='INCOTERM', help="International Commercial Terms are a series of predefined commercial terms used in international transactions.")
					
	@api.multi
	def name_get(self):
		TYPES = {
			'out_invoice': _('Invoice'),
			'in_invoice': _('Supplier Invoice'),
			'out_refund': _('Refund'),
			'in_refund': _('Supplier Refund'),
		}
		result = []
		for inv in self:
			#only use invoice.number as the name
			if self._context.get('show_cust_pi'):				
				result.append((inv.id, "%s %s" % (inv.number or TYPES[inv.type], inv.contact_n or '')))
			else:
				result.append((inv.id, inv.number or TYPES[inv.type]))
		return result	
	
	@api.multi
	def onchange_payment_term_date_invoice(self, payment_term_id, date_invoice):
		resu = super(account_invoice, self).onchange_payment_term_date_invoice(payment_term_id, date_invoice)
		#johnw, 2015/11/10, set date invoice to date due, it is the current date, ref super.onchange_payment_term_date_invoice() for detail.
		if not payment_term_id:
			resu['value']['date_invoice'] = resu['value']['date_due']
		return resu
	
	@api.model
	def name_search(self, name, args=None, operator='ilike', limit=100):
		args = args or []
		recs = self.browse()
		if name:
			recs = self.search([('number', '=', name)] + args, limit=limit)
		if not recs:
			#johnw, 2015/11/10, for the number, use 'operator'
			#recs = self.search([('name', operator, name)] + args, limit=limit)
			recs = self.search(['|','|','|',('name', operator, name),('number', operator , name),('contract_n', operator , name),('origin', operator , name)] + args, limit=limit)
		return recs.name_get()	
	
	#field link to generated customer invoice
	cust_inv_id = fields.Many2one('account.invoice', string='Customer Invoice', readonly=True, copy=False)
	
	@api.multi
	def invoice_sup2cust(self):
		assert len(self) == 1, 'This option should only be used for a single id at a time.'
		'''
			Customer: first product's customer
			Journal: Sales Journal
			Invoice Date: current date
			Account: AP/AR
			Line's account		
		'''
		#invoice type
		inv_type = self.type=='in_invoice' and 'out_invoice' or 'out_refund'
		#customer id:
		customer = None
		if self.invoice_line:
			for inv_line in self.invoice_line:
				if inv_line.product_id.customer_id:
					customer = inv_line.product_id.customer_id
		if not customer:
			raise except_orm(_('Error!'),
		        _('Please define add invoice line and set the customer to the products.'))
		#journal: sales journal
		sale_journal = self.env['account.journal'].search([('type', '=', 'sale'), ('company_id', '=', self.company_id.id)],limit=1)
		if not sale_journal:
			raise except_orm(_('Error!'),
		        _('Please define sales journal for this company: "%s" (id:%d).') % (self.company_id.name, self.company_id.id))
		#invoie date
		date_invoice = fields.Date.context_today(self)
		#account
		account_id = customer.property_account_receivable.id
		#generate customer invoice
		cust_inv = self.copy({'type':inv_type, 
								'partner_id': customer.id, 
								'journal_id': sale_journal.id, 
								'date_invoice':date_invoice,
								'account_id':account_id})
		#update customer invoice line's account
		for inv_line in cust_inv.invoice_line:
			account_id = inv_line.product_id.property_account_income.id
			if not account_id:
				account_id = inv_line.product_id.categ_id.property_account_income_categ.id
			if not account_id:
				raise except_orm(_('Error!'),
						_('Please define income account for this product: "%s" (id:%d).') % \
							(inv_line.product_id.name, inv_line.product_id.id,))
			inv_line.write({'account_id':account_id})
		#update supplier invoice's customer invoice id
		self.write({'cust_inv_id':cust_inv.id})
		#goto customer invoice
		res = self.env['ir.model.data'].get_object_reference('account', 'invoice_form')
		res_id = res and res[1] or False
		return {
			'name': _('Customer Invoice'),
			'view_type': 'form',
			'view_mode': 'form',
			'view_id': [res_id],
			'res_model': 'account.invoice',
			'context': "{'type':'out_invoice', 'journal_type': 'sale'}",
			'type': 'ir.actions.act_window',
			'nodestroy': True,
			'target': 'current',
			'res_id': cust_inv.id,
		}

	def invoice_pay_customer(self, cr, uid, ids, context=None):
		resu = super(account_invoice,self).invoice_pay_customer(cr, uid, ids, context=context)
		ref = None
		inv = self.browse(cr, uid, ids[0], context=context)
		#inv.name is the po/so name
		ref = inv.name
#		if inv.type in('out_invoice','out_refund'):
#			ref = inv.contract_n
#		if inv.type == 'in_invoice':
#			ref = inv.origin
#		if inv.type == 'in_refund':
#			ref = inv.name
		if ref:
			resu['context']['default_reference'] = ref
		return resu
	
#Credit/Debit note numer generation
class account_move(models.Model):
	_inherit="account.move"
	def post(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		invoice = context.get('invoice', False)
		valid_moves = self.validate(cr, uid, ids, context)

		if not valid_moves:
			raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
		obj_sequence = self.pool.get('ir.sequence')
		for move in self.browse(cr, uid, valid_moves, context=context):
			if move.name =='/':
				new_name = False
				journal = move.journal_id

				if invoice and invoice.internal_number:
					new_name = invoice.internal_number
				else:
					if journal.sequence_id:
						c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
						#johnw, change to use the refund journal to get the name
						#new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
						inv = None
						inv_ids = self.pool['account.invoice'].search(cr, uid, [('move_id', '=', move.id)], context=context)
						if inv_ids:
							inv = self.pool['account.invoice'].browse(cr, uid, inv_ids, context=context)[0]
						ctx_inv = context.copy()
						ctx_inv['active_test'] = False
						journal_obj = self.pool['account.journal']
						if inv and inv.type == 'out_refund':
							journal_seq_ids = journal_obj.search(cr, uid, [('type','=','sale_refund')], context=ctx_inv)
							if journal_seq_ids:
								journal_seq = journal_obj.browse(cr, uid, journal_seq_ids[0], context=ctx_inv)
								new_name = obj_sequence.next_by_id(cr, uid, journal_seq.sequence_id.id, c)
						elif inv and inv.type == 'in_refund':
							journal_seq_ids = journal_obj.search(cr, uid, [('type','=','purchase_refund')], context=ctx_inv)
							if journal_seq_ids:
								journal_seq = journal_obj.browse(cr, uid, journal_seq_ids[0], context=ctx_inv)
								new_name = obj_sequence.next_by_id(cr, uid, journal_seq.sequence_id.id, c)
						else:
							new_name = obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)							
					else:
						raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))

				if new_name:
					self.write(cr, uid, [move.id], {'name':new_name})

		cr.execute('UPDATE account_move '\
				   'SET state=%s '\
				   'WHERE id IN %s',
				   ('posted', tuple(valid_moves),))
		self.invalidate_cache(cr, uid, context=context)
		return True	
	
from openerp.osv import osv
class sale_order(osv.osv):
	_inherit = 'sale.order'
	def _prepare_invoice(self, cr, uid, order, lines, context=None):
		vals = super(sale_order, self)._prepare_invoice(cr, uid, order, lines, context=context)
		vals.update({'incoterm':order.incoterm and order.incoterm.id or None})	
		return vals
#po_super.STATE_SELECTION = STATE_SELECTION_PO	