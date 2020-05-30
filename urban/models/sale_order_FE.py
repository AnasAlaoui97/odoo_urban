# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare



from werkzeug.urls import url_encode

           


class SaleOrder(models.Model):
    _inherit = "sale.order"

    nameFE = fields.Char(string='Réf#', readonly=True, default="Nouvelle")
    interloc = user_id = fields.Many2one('res.users', string='Interlocuteur', index=True, tracking=2, default=lambda self: self.env.user)
    objet = fields.Char(string='Objet')
    delai_liv = fields.Datetime(string='Délai de livraison')
    observ = fields.Text(string='Observations')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('doneFE', "Fiche d'exécution"),
        ('cancel', 'Cancelled')
        ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')
    element_asso = fields.Selection([
        ('normal', 'Maquette'),
        ('phantom', 'CSP'),
        ('autres', 'Autres')], "Eléments associés",
        default='normal', required=True)

    def action_print(self):
        return self.env.ref('sale.action_report_sale_FE').report_action(self)
    def action_FE(self):
        self.write({'state': 'doneFE'})
    def action_annulerFE(self):
        self.write({'state': 'sale'})

 

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'


    decor = fields.Char(string='Décor')
    dimensions = fields.Char(string='Dimensions')
    mat_epai = fields.Char(string='Matière/epaisseur')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Done'),
        ('doneFE', "Fiche d'exécution"),
        ('cancel', 'Cancelled')
    ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')
