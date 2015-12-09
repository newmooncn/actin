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

from openerp import models, fields, api

class account_invoice(models.Model):
	_inherit = "account.invoice"
	
	origin_inv_id = fields.Many2one('account.invoice', string='Original Invoice',
        ondelete='restrict', index=True)
	
	@api.model
	def _prepare_refund(self, invoice, date=None, period_id=None, description=None, journal_id=None):
		resu = super(account_invoice, self)._prepare_refund(invoice, date=date, period_id=period_id,description=description,journal_id=journal_id)
		resu.update({'origin_inv_id':invoice.id})
		return resu

from openerp.osv import osv
class account_invoice_refund(osv.osv_memory):
	_inherit = "account.invoice.refund"	
	def _get_journal(self, cr, uid, context=None):
		obj_journal = self.pool.get('account.journal')
		user_obj = self.pool.get('res.users')
		if context is None:
			context = {}
		inv_type = context.get('type', 'out_invoice')
		company_id = user_obj.browse(cr, uid, uid, context=context).company_id.id
		#johnw, 2015/12/09
		'''
		type = (inv_type == 'out_invoice') and 'sale_refund' or \
			   (inv_type == 'out_refund') and 'sale' or \
			   (inv_type == 'in_invoice') and 'purchase_refund' or \
			   (inv_type == 'in_refund') and 'purchase'
		'''
		type = inv_type in ('out_invoice','out_refund') and 'sale' or  inv_type in ('in_invoice','in_refund') and 'purchase'
		journal = obj_journal.search(cr, uid, [('type', '=', type), ('company_id','=',company_id)], limit=1, context=context)
		return journal and journal[0] or False	
	
	_defaults = {
		'journal_id': _get_journal,
	}		
