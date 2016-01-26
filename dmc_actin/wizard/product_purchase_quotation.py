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
from openerp.addons.dm_rubylong import get_rubylong_fields_xml, get_rublong_data_url, get_rubylong_fields_xml_body
from string import upper

class product_sale_offer(osv.osv_memory):
    _name = 'product.purchase.quotation'
    _description = 'Product purchase quotation'

    def _get_rubylong_xml(self, cr, uid, ids, field_names, args, context=None):
        if isinstance(ids, (int, long)):
            ids = [ids]
        res = {}
        for po_id in ids:
            res[po_id] = ''
        data_xml = ''
        order_main = None
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            order_xml = ''
            if not order_main:
                order_main = order
            order_fields = [
                        ('id','product_id'),
                        'company_id.name',
                        'company_id.street',
                        'company_id.street2',
                        'company_id.city',
                        'company_id.country_id.name',
                        'company_id.contact',
                        'company_id.phone',
                        'company_id.fax',
                        'company_id.email',
                        ('company_id.logo','company_logo'),
                        
                        'name',
                        ('default_code','code'),
                        'image',
                        'description',
                        
                        'tech_data',
                        
                        'certificate',
                        'labor',
                        
                        'dimension',
                        ('weight_char','weight_gross'),
                        ('weight_net_char','weight_net'),
                        'pack_out_dimension',
                        'pack_out_volume',
                        ('pack_out_gw','pack_out_weight_gross'),
                        
                        'qty_20gp',
                        'qty_40gp',
                        'qty_40hq',
                        'qty_pallet_eur',
                        'qty_pallet_us',
                        
                        'quote_validity',
                        'additional_comments',
                        
                        #vendor data
                        ('seller_id.name','partner_name'),
                        ('seller_id.contact','partner_contact'),
                    
                        ('standard_price','price_unit'),
                                                
                        #added by customer
                        ('standard_price_curr_id.name','currency_name'),
                        ('incoterm_id.name','incoterm'),
                        ('seller_payment_term_id.name','payment_term',)
                        ]
            order_xml += get_rubylong_fields_xml_body(order.product_id, order_fields)

            #vendor data
            order_fields = [
                        ('pr_number','order_name'),
                        'date_order',
                        ]
            order_xml += get_rubylong_fields_xml_body(order, order_fields)            
            
            #final xml for this order
            data_xml = "<%s>%s</%s>"%('header', order_xml, 'header')  
        
        #write data
        if order_main:
            res[order_main.id] = get_rublong_data_url(order_main,data_xml,cr.dbname)
        return res
            
    _columns = {
        'product_id': fields.many2one('product.product', 'Product'),
        'is_service': fields.boolean('Is Service'),
        'name': fields.related('product_id', 'name', type='char', size=128, string = 'Product Name'),
        'pr_number': fields.char('PR NUMBER'),
        'date_order':fields.date('Date'),
        'rubylong_xml_file':fields.function(_get_rubylong_xml, type='text', string='Rubylong xml')
    }
    
    def default_get(self, cr, uid, fields_list, context=None):
        vals = super(product_sale_offer,self).default_get(cr, uid, fields_list, context)
        if context.get('active_model') == 'product.product':
            vals.update({'product_id':context.get('active_id')})
        vals['date_order'] = fields.date.context_today(self,cr,uid,context=context)
        return vals    
            
product_sale_offer()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

