# -*- encoding: utf-8 -*-
##############################################################################
#
#    OGO Process Improvements Module
#    Copyright (C) 2012 OGO (<http://www.odoogo.com>).
#
##############################################################################
{
    'name': 'DMC ACTIN',
    'version': '1.0',
    'category': 'Customization',
    'author': 'DMEMS',
    'website': 'www.dmems.com',
    'description': """
ACTIN Customization
=====================
* Add fields to product sheet
* Add fields to partner sheet
* Rename menu names
* Remove tax on purchase, sale and invoice
* Add below fields to purchase order
'client_order_ref': for the customer order refererence
port_load_id, port_discharge_id,deliver_dates,ship_type,penalties_on_delays,discrepancy,disputes,doc_export,confirmation,artworks
certs, qc_memo, load_memo, 
* Purchase: Remove 'remove RFQ&B' page, add 'Terms' page
* Purchase: Remove the state showing for 'RFQ'/'Bid Received'
* Purchase: PO PDF
* Purchase: Convert to SO
* Sales Order: new fields
* Sales Order: PDF  
    """,
    'depends': ['base','dm_base', 'product', 'sale', 'purchase', 'sale_stock', 'dmp_product',
                'dmp_prod_supplier', 'dm_options', 'dmp_account_pay_invoice', 'dmp_account_rpt_account',
                'dmp_prod_customer',"account_voucher","dmp_account_move_source","dm_rubylong"],
    'data':['security/ir.model.access.csv',
            'report/product_sale_offer_view.xml',
            'report/report_saleorder.xml',
            'report_rubylong.xml', 'product_view.xml', 'menu.xml', 'partner_view.xml', 'tax_remove_view.xml', 
            'purchase_view.xml', 'sale_view.xml', 'invoice_view.xml',
            'packing_view.xml','invoice_refund.xml','account_view.xml','account_rpt_view.xml',
            ],
    'auto_install': False,
    'installable': True

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
