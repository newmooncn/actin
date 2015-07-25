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
	contract_n = fields.Char('CONTRACT N', size=64)
	bl_number = fields.Char('BL NUMBER', size=64)
	container_no = fields.Char('CONTAINER No', size=64)
	seal_no = fields.Char('SEAL No', size=64)
	serial_no = fields.Text('SERIAL No')
	hs_code = fields.Char('HS CODE', size=64)
	#new fields for estimated deliver an arrival
	etd = fields.Date('ETD')
	eta = fields.Date('ETA')
	#used for service invoice, related to the commercial invoice
	parent_id = fields.Many2one('account.invoice', 'Related Invoice', select=True)	
	child_ids = fields.One2many('account.invoice', 'parent_id', 'Service Invoices')
	
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
#po_super.STATE_SELECTION = STATE_SELECTION_PO	