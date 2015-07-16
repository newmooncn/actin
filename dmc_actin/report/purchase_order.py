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

class purchase_order_print(rml_parser_ext):
    def __init__(self, cr, uid, name, context):
        super(purchase_order_print, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
#            'get_pick_out_mo': self.get_pick_out_mo,
#            'get_bom_qty': self.get_bom_qty,
#            'get_product_customer_name': self.get_product_customer_name,
#            'get_product_supplier_name': self.get_product_supplier_name,
#            'get_product_desc': self.get_product_desc,
        })

report_sxw.report_sxw('report.purchase.order.actin',
                      'purchase.order',
                      'addons/dmc_actin/report/purchase_order.rml',
                      parser=purchase_order_print)
