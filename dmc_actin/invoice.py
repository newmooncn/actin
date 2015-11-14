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
class account_invoice(models.Model):
	_inherit="account.invoice"
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
												('quanlity','Quanlity control'),
												('laboratory','Laboratory'),
												('audit','Audit'),
												('accounting','Accounting'),
												('procurement','Procurement'),
												('sourcing','Sourcing'),
												('others','Others')),
									string='Service type')		 
	 
	parent_id = fields.Many2one('account.invoice', 'Commercial Invoice', select=True, domain="[('is_service','=',False),('type','=','out_invoice')]")	
	child_ids = fields.One2many('account.invoice', 'parent_id', 'Service Invoices')
	
	#fields for loading/discharge ports

#	@api.one
#	@api.depends('sale_ids')
#	def _sale_info(self):
#		so = self.sale_ids and self.sale_ids[0] or False
#		if so:
#			self.port_load_id = so.port_load_id.id
#			self.port_discharge_id = so.port_discharge_id.id
#		
#	port_load_id = fields.Many2one('option.list', string='Port of loading', 
#								domain=[('option_name','=','partner_port')], 
#								readonly=True,
#								compute='_sale_info', 
#								store=True)
#	port_discharge_id = fields.Many2one('option.list', string='Port of discharge', 
#								domain=[('option_name','=','partner_port')], 
#								readonly=True,
#								compute='_sale_info', 
#								store=True)
	
	#will be set in sale.py._prepare_invoice()
	port_load_id = fields.Many2one('option.list', string='Port of loading', domain=[('option_name','=','partner_port')])
	port_discharge_id = fields.Many2one('option.list', string='Port of discharge', domain=[('option_name','=','partner_port')])
	
	#fields for the service flag
	is_service = fields.Boolean('Service')
					
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
			#result.append((inv.id, "%s %s" % (inv.number or TYPES[inv.type], inv.name or '')))
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
			recs = self.search(['|',('name', operator, name),('number', operator , name)] + args, limit=limit)
		return recs.name_get()	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	