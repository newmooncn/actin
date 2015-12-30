# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


import time
from openerp.report import report_sxw
from openerp.addons.dm_base.rml import rml_parser_ext

class po_print(rml_parser_ext):
    def __init__(self, cr, uid, name, context):
        super(po_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'qty_total': self.qty_total,
        })
        
    def qty_total(self, order):
        qty = 0
        for line in order.order_line:
            qty += line.product_qty
        return qty

report_sxw.report_sxw('report.purchase.order.actin',
                      'purchase.order',
                      'addons/dmc_actin/report/purchase_order.rml',
                      parser=po_print)

class pi_print(rml_parser_ext):
    def __init__(self, cr, uid, name, context):
        super(pi_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'qty_total': self.qty_total,
            'qty_total_uom': self.qty_total_uom,
        })
        
    def qty_total(self, order):
        qty = 0
        uoms = {}
        for line in order.order_line:
            qty += line.product_uom_qty
            if line.product_uom.id not in uoms:
                uoms[line.product_uom.id] = line.product_uom.name
        
        return qty
        
    def qty_total_uom(self, order):
        uoms = {}
        for line in order.order_line:
            if line.product_uom.id not in uoms:
                uoms[line.product_uom.id] = line.product_uom.name
        
#        uom uoms.keys
#        print len(uoms.keys)
        if len(uoms) == 1:
            return uoms.values()[0]
        else:
            return ''
    
report_sxw.report_sxw('report.proforma.invoice.actin',
                      'sale.order',
                      'addons/dmc_actin/report/sale_order.rml',
                      parser=pi_print)

class invoice_print(rml_parser_ext):
    def __init__(self, cr, uid, name, context):
        super(invoice_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'so': self.sale_order,
            'po': self.purchase_order,
            'qty_total': self.qty_total,
        })
    def sale_order(self, inv):
        so = inv.sale_ids and inv.sale_ids[0] or False
        #origin_inv_id is from invoice_refund.py
        if not so and inv.origin_inv_id:
            #for customer refund / credit note
            so = self.sale_order(inv.origin_inv_id)
        return so
            
    def purchase_order(self, inv):
        po = inv.purchase_ids and inv.purchase_ids[0] or False
        #origin_inv_id is from invoice_refund.py
        if not po and inv.origin_inv_id:
            #for supplier refund / debit note
            po = self.purchase_order(inv.origin_inv_id)
        return po
    
    def qty_total(self, inv):
        qty = 0
        for line in inv.invoice_line:
            qty += line.quantity
        return qty

report_sxw.report_sxw('report.commercial.invoice.actin',
                      'account.invoice',
                      'addons/dmc_actin/report/sale_commercial_invoice.rml',
                      parser=invoice_print)
report_sxw.report_sxw('report.packing.list',
                      'account.invoice',
                      'addons/dmc_actin/report/packing_list.rml',
                      parser=invoice_print)
report_sxw.report_sxw('report.debit.note',
                      'account.invoice',
                      'addons/dmc_actin/report/debit_note.rml',
                      parser=invoice_print)