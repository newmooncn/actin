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

report_sxw.report_sxw('report.purchase.order.actin',
                      'purchase.order',
                      'addons/dmc_actin/report/purchase_order.rml',
                      parser=rml_parser_ext)

report_sxw.report_sxw('report.proforma.invoice.actin',
                      'sale.order',
                      'addons/dmc_actin/report/sale_order.rml',
                      parser=rml_parser_ext)

class invoice_print(rml_parser_ext):
    def __init__(self, cr, uid, name, context):
        super(invoice_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'so': self.sale_order,
#            'po': self.purchase_order,
        })
    def sale_order(self, inv):
        return inv.sale_ids and inv.sale_ids[0] or False
#    def purchase_order(self, inv):
#        return inv.purchase_ids and inv.purchase_ids[0] or False

report_sxw.report_sxw('report.commercial.invoice.actin',
                      'account.invoice',
                      'addons/dmc_actin/report/sale_commercial_invoice.rml',
                      parser=invoice_print)