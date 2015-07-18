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
class account_invoice(osv.osv):
	_inherit="account.invoice"
	_columns = {
		#new fields on PDF
		'total_shipped': fields.char('TOTAL SHIPPED', size=64),
		'contract_n': fields.char('CONTRACT N', size=64),
		'bl_number': fields.char('BL NUMBER', size=64),
		'container_no': fields.char('CONTAINER No', size=64),
		'seal_no': fields.char('SEAL No', size=64),
		'serial_no': fields.text('SERIAL No'),
		'hs_code': fields.char('HS CODE', size=64),
		#new fields for estimated deliver an arrival
		'etd': fields.date('ETD'),
		'eta': fields.date('ETA'),
	}
	
#po_super.STATE_SELECTION = STATE_SELECTION_PO	