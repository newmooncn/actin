# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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


class product_sale_offer(osv.osv_memory):
    _name = 'product.sale.offer'
    _description = 'Product sale offer'
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'prod_cust_id': fields.many2one('product.customerinfo', 'Customer', required=True, domain="[('product_id','=',product_id)]")
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        vals = super(product_sale_offer,self).default_get(cr, uid, fields_list, context)
        if context.get('active_model') == 'product.product':
            vals.update({'product_id':context.get('active_id')})
        return vals    
    
    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        res = self.read(cr, uid, ids, ['product_id','partner_id'], context=context)
        res = res and res[0] or {}
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'product.sale.offer',
            'datas': {'ids': ids, 'form':res},
       }
product_sale_offer()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

