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

class res_partner(osv.Model):
    _inherit = 'res.partner'
    _columns = {
        'incoterm_id': fields.many2one('stock.incoterms', 'Incoterm', 
                                    help="International Commercial Terms are a series of predefined commercial terms used in international transactions."),
        'port': fields.many2one('option.list','Port', ondelete='restrict', domain=[('option_name','=','partner_port')]),        
        'exp_company': fields.char('Express company'),
        'exp_comp_act': fields.char('Express account number'),
        'forwarder': fields.char('Forwarder'),

    }
    
class res_partner_bank(osv.osv):
    '''Bank Accounts'''
    _inherit = "res.partner.bank"
    _columns = {       
        'bank_swift': fields.char('Bank Swift Code'),
    }