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


class FE(models.Model):
    _name = "urban.fiche"
    _description = "Fiche d'execution"

    name = fields.Char(string='Réf#', readonly=True, default="Nouvelle")
    fiche_line_ids = fields.One2many('urban.line.fiche', 'fiche_id',
                                         string="Fiche lines", auto_join=True, readonly=True, states={'draft': [('readonly', False)]})

    date_commande = fields.Date(string='Date', readonly=True, states={'draft': [('readonly', False)]})
    commande_id = fields.Many2one('sale.order', string='Commande associée', domain="[('state', '=', 'sale')]",
                                  readonly=True, states={'draft': [('readonly', False)]}, required=True)


    client = fields.Many2one('res.partner', string='Client', readonly=True, states={'draft': [('readonly', False)]})
    interloc = fields.Many2one('res.users', string='Interlocuteur', index=True, tracking=2,
                               readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.user)
    coordonnees = fields.Char(string='Coordonnées', readonly=True, states={'draft': [('readonly', False)]})

    objet = fields.Char(string='Objet', readonly=True, states={'draft': [('readonly', False)]})
    delai_liv = fields.Datetime(string='Délai de livraison', readonly=True, states={'draft': [('readonly', False)]})

    element_asso = fields.Selection([
        ('aucun', ' '),
        ('normal', 'Maquette'),
        ('phantom', 'CSP'),
        ('autres', 'Autres')], "Eléments associés",
        default='aucun', readonly=True, states={'draft': [('readonly', False)]})

    observ = fields.Text(string='Observations', readonly=True, states={'draft': [('readonly', False)]})

    mo_count = fields.Integer(string="Ordres de fabrications", compute='mo_count_fe')
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('ok', "Fiche d'exécution"),
        ('done', "Fiche d'exécution traitée")
    ], string='Etat', readonly=True, copy=False, index=True, tracking=3, default='draft')


    def open_fe(self):
        return {
            'name': _('Ordre de fabrications'),
            'domain': [('fe_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'mrp.production',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def mo_count_fe(self):
        c = self.env['mrp.production'].search_count([('fe_id', '=', self.id)])
        self.mo_count = c

    def action_open(self):
        a = self.env['ir.sequence'].next_by_code('urban.fiche') or _('0001')
        self.write({'state': 'ok', 'name': a})

    def action_ok(self):
        self.write({'state': 'done'})

    def action_print(self):
        return self.env.ref('urban.action_report_sale_FE').report_action(self)


class FELine(models.Model):
    _name = "urban.line.fiche"
    _description = "Line fiche d'execution"

    name = fields.Char(string='Réf#', default="/")
    fiche_id = fields.Many2one('urban.fiche', string='Fiche_', required=True)

    n_prix = fields.Integer(string='N.Prix')
    product_code = fields.Many2one('product.product',string='Article', required=True)
    decor = fields.Char(string='Décor')
    dimensions = fields.Char(string='Dimensions')
    mat_epai = fields.Char(string='Matière/epaisseur')
    qty = fields.Float(string='Quantité', digits=(5,2), required=True, default=0.0)


#  inherit ordre fab
class MrpProduction(models.Model):
    _inherit = "mrp.production"

    fe_id = fields.Many2one('urban.fiche', string="Fiche d'exécution associée", domain="[('state', '=', 'ok')]")


#  inherit sale order
class SaleOrder(models.Model):
    _inherit = "sale.order"

    fe_count = fields.Integer(string="Fiches d'exécution", compute='fe_count_so')

    def open_so_fe(self):
        return {
            'name': _("Fiches d'exécution"),
            'domain': [('commande_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'urban.fiche',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def fe_count_so(self):
        c = self.env['urban.fiche'].search_count([('commande_id', '=', self.id)])
        self.fe_count = c