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

class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns={
        #the fields only for search usage
        'date_search_from':fields.function(lambda *a,**k:{}, type='date',string="From Date",),
        'date_search_to':fields.function(lambda *a,**k:{}, type='date',string="To Date",), 
        }
    def search(self, cr, user, args, offset=0, limit=None, order=None, context=None, count=False):
        for arg in args:
            if arg[0] == 'date_search_from':
                arg[0] = 'date'
                arg[1] = '>='
            if arg[0] == 'date_search_to':
                arg[0] = 'date'
                arg[1] = '<='
        
        return super(account_move_line,self).search(cr, user, args, offset, limit, order, context, count) 
        
#po_super.STATE_SELECTION = STATE_SELECTION_PO	