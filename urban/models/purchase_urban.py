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


# Service
class Service(models.Model):
    _name = "urban.service"
    _description = "Service"

    name = fields.Char(string='Service', required=True)
    note = fields.Text(string='Description', required=False)

# Lieu de livraison
class LieuLivraison(models.Model):
    _name = "urban.lieu_livraison"
    _description = "Lieu de livraison"

    name = fields.Char(string='Lieu de livraison', required=True)
    note = fields.Text(string='Description', required=False)


# Demande d'achat
class Demandedachat(models.Model):
    _name = "urban.demandedachat"
    _description = "Demande d'achat"

    name = fields.Char(string='Réf#', readonly=True, default="Nouvelle")

    service_id = fields.Many2one('urban.service', string='Service Demandeur', index=True, required=True,
                                 readonly=True, states={'draft': [('readonly', False)]})
    livraison_id = fields.Many2one('urban.lieu_livraison', string='Lieu de livraison', required=True,
                                   readonly=True, states={'draft': [('readonly', False)]})

    stock = fields.Boolean(string="Stock", readonly=True, states={'draft': [('readonly', False)]})
    user = fields.Boolean(string="Utilisateur", readonly=True, states={'draft': [('readonly', False)]})

    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    date = fields.Date(string='Date', readonly=True, default=fields.Datetime.now)
    receptionist = fields.Char(string='Nom de receptionnaire', readonly=True, states={'draft': [('readonly', False)]})

    justification = fields.Text(string="Justification du besoin d'achat", readonly=True, states={'draft': [('readonly', False)]})

    demandedachat_line_ids = fields.One2many('urban.line.demandedachat', 'demandedachat_id',
                                             string="Demande d'achat lines", auto_join=True, readonly=True,
                                             states={'draft': [('readonly', False)]})

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('inprogress', "Demande envoyée"),
        ('done', 'Demande validée'),
        ('cancel', 'Demande refusée'),
        ], string='Etat', readonly=True, default='draft')


    def action_open(self):
        a = self.env['ir.sequence'].next_by_code('urban.demandedachat') or _('0001')
        self.write({'state': 'inprogress', 'name': a})

    def action_done(self):
        self.write({'state': 'done'})

    def action_print(self):
        return self.env.ref('purchase.action_report_urban_demandedachat').report_action(self)

    def action_retour(self):
        self.write({'state': 'draft'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

# line bon d'achat
class Linedemandedachat(models.Model):
    _name = "urban.line.demandedachat"
    _description = "Line Demande dachat"


    name = fields.Char(string='Réf#', default="/")
    demandedachat_id = fields.Many2one('urban.demandedachat', string='Demande_', required=True)
    product_id = fields.Many2one('product.product', string='Article', required=True)
    unit_id = fields.Many2one('uom.uom', string='Unité', required=True)
    qty = fields.Float('Quantité Demandée', digits=(4, 2))
    date_souhaitee = fields.Date(string='Date de livraison souhaitée')




