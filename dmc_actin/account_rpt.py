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

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class account_rpt(osv.osv):
    _name = "account.rpt"
    _table = "account_rpt_view"
    _description = "ACTIN FINANCE REPORT"
    _auto = False   
    _rec_name = 'pi_name'
    _columns = {                
        'id': fields.float('ID'),
        'so_id': fields.many2one('sale.order',u'Proforma Invoice'),
        'ci_id': fields.many2one('account.invoice',u'Commercial Invoice'),
        'po_id': fields.many2one('purchase.order',u'Puchase Order'),
        'po_inv_id': fields.many2one('account.invoice',u'Factory CI'),
        
        'pi_date': fields.date('Actin Proforma Date'),        
        'pi_name': fields.char('Actin Proforma Number'),
        'ci_date': fields.date('Actin Invoice Date'),        
        'ci_name': fields.char('Actin Invoice Number'),
        'customer_id': fields.many2one('res.partner','Customer'),
        'pi_note': fields.char('Product Description'),
        'pi_amount': fields.float('Actin Proforma Amount', digits_compute= dp.get_precision('Account')),
        'ci_amount': fields.float('Actin Invoice Amount', digits_compute= dp.get_precision('Account')),
        
        'supplier_id': fields.many2one('res.partner','Factory'),
        'po_date': fields.date('Factory Contract Date'),        
        'po_name': fields.char('Factory contract Number'),
        'po_amount': fields.float('Factory Contract Amount', digits_compute= dp.get_precision('Account')),  
        #'po_inv_name': fields.char('Factory Invoice Number'),      
        'po_inv_date': fields.date('Factory Invoice Date'),        
        'po_inv_amount': fields.float('Factory Invoice Amount', digits_compute= dp.get_precision('Account')),
                
        'so_incoterm_id': fields.many2one('stock.incoterm','Incoterm'),

        'trans_sf_partner_id': fields.many2one('res.partner','TPS Company'),
        'trans_sf_amount': fields.float('TPS Sea Freight amount', digits_compute= dp.get_precision('Account')),  
        'trans_sf_date': fields.date('TPS SF Invoice date'), 
        'trans_sf_date_pay': fields.date('TPS SF Invoice payment date'),       
        
        #'trans_dc_partner_id': fields.many2one('res.partner','TPS Company'),
        'trans_dc_amount': fields.float('TPS Destination charges amount', digits_compute= dp.get_precision('Account')),  
        'trans_dc_date': fields.date('TPS DC Invoice date'), 
        'trans_dc_date_pay': fields.date('TPS DC Invoice payment date'),    

        'qc_partner_id': fields.many2one('res.partner','QC Company'),
        'qc_amount': fields.float('QC Amount', digits_compute= dp.get_precision('Account')),
        #'qc_date': fields.date('QC Invoice date'),   
        'sale_margin': fields.float('Brut Mergin', digits_compute= dp.get_precision('Account')),        
    }

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_rpt_view')
        cr.execute("""
            create or replace view account_rpt_view as (
select
((coalesce(so.id,0)::varchar)||coalesce(so_inv.id,0)::varchar||coalesce(po.id,0)::varchar||coalesce(po_inv.id,0)::varchar||coalesce(trans_sf.id,0)::varchar||coalesce(trans_dc.id,0)::varchar||coalesce(qc.id,0)::varchar)::NUMERIC as id,
so.id as so_id,
so_inv.id as ci_id,
po.id as po_id,
po_inv.id as po_inv_id,

so.date_order as pi_date,
so.name as pi_name,
so_inv.date_invoice as ci_date,
so_inv.number as ci_name,
so_inv.partner_id as customer_id,
so.note as pi_note,
so.amount_total as pi_amount,
so_inv.amount_total as ci_amount,

po.partner_id as supplier_id,
po.date_order as po_date,
po.name as po_name,
po.amount_total as po_amount,
po_inv.number as po_inv_name,
po_inv.date_invoice as po_inv_date,
po_inv.amount_total as po_inv_amount,

so.incoterm as so_incoterm_id,

trans_sf.partner_id as trans_sf_partner_id,
trans_sf.amount_total as trans_sf_amount,
trans_sf.date_invoice as trans_sf_date,
trans_sf_pay.date as trans_sf_date_pay,

trans_dc.partner_id as trans_dc_partner_id,
trans_dc.amount_total as trans_dc_amount,
trans_dc.date_invoice as trans_dc_date,
trans_dc_pay.date as trans_dc_date_pay,

qc.partner_id as qc_partner_id,
qc.amount_total as qc_amount,
qc.date_invoice as qc_date,

(so_inv.amount_total - po_inv.amount_total - trans_sf.amount_total - trans_dc.amount_total - qc.amount_total) as sale_margin

--so.name,po.name,so_inv.name,trans_sf.name,trans_dc.name,qc.name

from sale_order so
left join sale_order_invoice_rel so_inv_rel on so.id = so_inv_rel.order_id
left join account_invoice so_inv on so_inv_rel.invoice_id = so_inv.id

left join purchase_order po on so.id = po.sale_id
left join purchase_invoice_rel po_inv_rel on po.id = po_inv_rel.purchase_id
left join account_invoice po_inv on po_inv_rel.invoice_id = po_inv.id

left join account_invoice trans_sf on trans_sf.parent_id = so_inv.id and trans_sf.ci_service_type = 'trans_sea'
left join account_voucher trans_sf_pay on trans_sf.id = trans_sf_pay.invoice_id

left join account_invoice trans_dc on trans_dc.parent_id = so_inv.id and trans_dc.ci_service_type = 'trans_dc'
left join account_voucher trans_dc_pay on trans_dc.id = trans_dc_pay.invoice_id

left join account_invoice qc on qc.parent_id = so_inv.id and qc.ci_service_type = 'quanlity'

order by so.id desc, so_inv.id, po.id, po_inv.id
            )
        """)               
account_rpt()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
