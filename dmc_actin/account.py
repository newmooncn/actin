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

class account_move(osv.osv):
    _inherit = "account.move"
    _columns={
        #the fields only for search usage
        'inv_name':fields.char("Invoice Number"),
        }
    
class account_move_line(osv.osv):
    _inherit = "account.move.line"
    _columns={
        #the fields only for search usage
        'date_search_from':fields.function(lambda *a,**k:{}, type='date',string="From Date",),
        'date_search_to':fields.function(lambda *a,**k:{}, type='date',string="To Date",), 
        'inv_name': fields.related('move_id', 'inv_name', string='Invoice Number', type='char', store=True),
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
        
#Purchase advance pay
class purchase_order(osv.osv):  
    _inherit = "purchase.order"
    def _prepare_payment_move(self, cr, uid, move_name, order, journal,
                              period, date, description, context=None):
        resu = super(purchase_order, self)._prepare_payment_move(cr, uid, move_name, order, journal,
                              period, date, description, context=context)
        resu['ref'] = order.sale_id and order.sale_id.name or ''
        resu['inv_name'] = order.name
        return resu
    
#Sale advance pay
class sale_order(osv.osv):  
    _inherit = "sale.order"
    def _prepare_payment_move(self, cr, uid, move_name, sale, journal,
                              period, date, description, context=None):
        resu = super(sale_order,self)._prepare_payment_move(cr,uid,move_name,sale,journal,period,date,description,context)
        resu.update({'inv_name':sale.name})
        return resu    
    
#Sales/Purchase invoice pay 
class account_voucher(osv.osv):
    _inherit = 'account.voucher'    
    def account_move_get(self, cr, uid, voucher_id, context=None):   
        resu = super(account_voucher, self).account_move_get(cr, uid, voucher_id, context=context)
        voucher = self.pool.get('account.voucher').browse(cr,uid,voucher_id,context)
        if voucher.invoice_id:
            inv = voucher.invoice_id
            if inv.type in('out_invoice','out_refund'):
                resu['inv_name'] = inv.number
                if inv.is_service:
                    #for service invoice, find related product CI, and then the related PI#
                    if inv.parent_id and inv.parent_id.sale_ids:
                        so = inv.parent_id.sale_ids
                        if isinstance(inv.parent_id.sale_ids, (list)):
                            so = so[0]
                        resu['ref'] = so.name

            if inv.type in('in_invoice','in_refund'):
                #set purchase pay's move's ref to related PI's name
                if not inv.is_service:
                    if voucher.invoice_id.purchase_ids:
                        po = voucher.invoice_id.purchase_ids[0]
                        if po.sale_id:
                            resu['ref'] = po.sale_id.name
                else:
                    #for service invoice, find related product CI, and then the related PI#
                    if inv.parent_id and inv.parent_id.sale_ids:
                        so = inv.parent_id.sale_ids
                        if isinstance(inv.parent_id.sale_ids, (list)):
                            so = so[0]
                        resu['ref'] = so.name
                    
                resu['inv_name'] = inv.supplier_invoice_number
        return resu
    
#invoice Validate for purchase and sale   
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    def action_move_create(self, cr, uid, ids, context=None):
        resu = super(account_invoice,self).action_move_create(cr, uid, ids, context=context)
        #get the move ids, and update resource_id
        move_obj = self.pool.get('account.move')
        for inv in self.browse(cr, uid, ids, context=context):
            move_vals = {}
            if inv.type in('out_invoice','out_refund'):
                move_vals.update({'inv_name':inv.number})
            if inv.type in('in_invoice','in_refund'):
                move_vals.update({'inv_name':inv.supplier_invoice_number})
                if inv.purchase_ids:
                    move_vals.update({'ref':inv.purchase_ids[0].name})
            move_obj.write(cr, uid, [inv.move_id.id],move_vals,context=context)
            #the related fields can not be updated sometime, update again
            self.pool['account.move.line'].write(cr, uid, [line.id for line in inv.move_id.line_id],move_vals,context=context)
        return resu        
#po_super.STATE_SELECTION = STATE_SELECTION_PO	